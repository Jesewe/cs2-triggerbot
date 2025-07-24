import os
import requests
import psutil
import sys
import subprocess
import pygetwindow as gw
import orjson
from packaging import version
from dateutil.parser import parse as parse_date

from classes.config_manager import COLOR_CHOICES
from classes.logger import Logger

# Initialize the logger for consistent logging
logger = Logger.get_logger()

class Utility:
    @staticmethod
    def fetch_offsets():
        """
        Fetches JSON data from two remote URLs and parses it using orjson.
        - Retrieves data from 'offsets.json' and 'client_dll.json' on GitHub.
        - Logs an error if either request fails or the server returns a non-200 status code.
        - Handles exceptions gracefully, ensuring no unhandled errors crash the application.
        """
        try:
            offsets_url = os.getenv(
                'OFFSETS_URL',
                'https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json'
            )
            response_offset = requests.get(offsets_url)

            client_dll_url = os.getenv(
                'CLIENT_DLL_URL',
                'https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json'
            )
            response_client = requests.get(client_dll_url)

            buttons_url = os.getenv(
                'BUTTONS_URL',
                'https://raw.githubusercontent.com/a2x/cs2-dumper/refs/heads/main/output/buttons.json'
            )
            response_buttons = requests.get(buttons_url)

            if response_offset.status_code != 200:
                logger.error("Failed to fetch offsets: offsets.json request failed.")
                return None, None

            if response_client.status_code != 200:
                logger.error("Failed to fetch offsets: client_dll.json request failed.")
                return None, None
            
            if response_buttons.status_code != 200:
                logger.error("Failed to fetch buttons: buttons.json request failed.")
                return None, None

            try:
                offset = orjson.loads(response_offset.content)
                client = orjson.loads(response_client.content)
                buttons = orjson.loads(response_buttons.content)
                return offset, client, buttons
            except orjson.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response: {e}")
                return None, None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None, None
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return None, None

    @staticmethod
    def check_for_updates(current_version):
        """Checks GitHub for the latest stable and pre-release versions and returns the download URL of 'VioletWing.exe' if an update is available."""
        try:
            # Fetch all releases to check both stable and pre-releases
            response = requests.get("https://api.github.com/repos/Jesewe/VioletWing/releases")
            response.raise_for_status()
            releases = orjson.loads(response.content)

            latest_stable = None
            latest_prerelease = None
            stable_download_url = None
            prerelease_download_url = None

            for release in releases:
                release_version = release.get("tag_name")
                if not release_version:
                    continue
                try:
                    parsed_version = version.parse(release_version)
                except version.InvalidVersion:
                    logger.warning(f"Invalid version format: {release_version}")
                    continue

                # Check if release is a pre-release
                is_prerelease = release.get("prerelease", False)
                for asset in release.get("assets", []):
                    if asset.get("name") == "VioletWing.exe":
                        download_url = asset.get("browser_download_url")
                        if download_url:
                            if is_prerelease:
                                if not latest_prerelease or parsed_version > version.parse(latest_prerelease):
                                    latest_prerelease = release_version
                                    prerelease_download_url = download_url
                            else:
                                if not latest_stable or parsed_version > version.parse(latest_stable):
                                    latest_stable = release_version
                                    stable_download_url = download_url

            current = version.parse(current_version)

            # Prioritize stable release if it's newer than current version
            if latest_stable and version.parse(latest_stable) > current:
                logger.info(f"New stable version available: {latest_stable}")
                return stable_download_url, False  # False indicates stable release
            # If no newer stable release, check pre-release
            elif latest_prerelease and version.parse(latest_prerelease) > current:
                logger.info(f"New pre-release version available: {latest_prerelease}")
                return prerelease_download_url, True  # True indicates pre-release
            else:
                logger.info("No new updates available.")
                return None, False

        except requests.exceptions.RequestException as e:
            logger.error(f"Update check failed: {e}")
            return None, False
        except Exception as e:
            logger.error(f"An unexpected error occurred during update check: {e}")
            return None, False

    @staticmethod
    def resource_path(relative_path):
        """Returns the path to a resource, supporting both normal startup and frozen .exe."""
        try:
            if hasattr(sys, '_MEIPASS'):
                return os.path.join(sys._MEIPASS, relative_path)
            return os.path.join(os.path.abspath("."), relative_path)
        except Exception as e:
            logger.error(f"Failed to get resource path: {e}")
            return None

    @staticmethod
    def is_game_active():
        """Check if the game window is active using pygetwindow."""
        windows = gw.getWindowsWithTitle('Counter-Strike 2')
        return any(window.isActive for window in windows)

    @staticmethod
    def is_game_running():
        """Check if the game process is running using psutil."""
        return any(proc.info['name'] == 'cs2.exe' for proc in psutil.process_iter(attrs=['name']))
    
    @staticmethod
    def extract_offsets(offsets: dict, client_data: dict, buttons_data: dict) -> dict | None:
        """Load memory offsets for game functionality."""
        try:
            client = offsets.get("client.dll", {})
            buttons = buttons_data.get("client.dll", {})
            classes = client_data.get("client.dll", {}).get("classes", {})

            def get_field(class_name, field_name):
                """Recursively search for a field in a class and its parents."""
                class_info = classes.get(class_name)
                if not class_info:
                    raise KeyError(f"Class '{class_name}' not found")

                field = class_info.get("fields", {}).get(field_name)
                if field is not None:
                    return field
                
                parent_class_name = class_info.get("parent")
                if parent_class_name:
                    return get_field(parent_class_name, field_name)
                    
                raise KeyError(f"'{field_name}' not found in '{class_name}' or its parents")

            extracted_offsets = {
                "dwEntityList": client.get("dwEntityList"),
                "dwLocalPlayerPawn": client.get("dwLocalPlayerPawn"),
                "dwLocalPlayerController": client.get("dwLocalPlayerController"),
                "dwViewMatrix": client.get("dwViewMatrix"),
                "dwForceJump": buttons.get("jump"),
                "m_iHealth": get_field("C_BaseEntity", "m_iHealth"),
                "m_iTeamNum": get_field("C_BaseEntity", "m_iTeamNum"),
                "m_pGameSceneNode": get_field("C_BaseEntity", "m_pGameSceneNode"),
                "m_vOldOrigin": get_field("C_BasePlayerPawn", "m_vOldOrigin"),
                "m_pWeaponServices": get_field("C_BasePlayerPawn", "m_pWeaponServices"),
                "m_iIDEntIndex": get_field("C_CSPlayerPawnBase", "m_iIDEntIndex"),
                "m_flFlashDuration": get_field("C_CSPlayerPawnBase", "m_flFlashDuration"),
                "m_pClippingWeapon": get_field("C_CSPlayerPawnBase", "m_pClippingWeapon"),
                "m_hPlayerPawn": get_field("CCSPlayerController", "m_hPlayerPawn"),
                "m_iszPlayerName": get_field("CBasePlayerController", "m_iszPlayerName"),
                "m_hActiveWeapon": get_field("CPlayer_WeaponServices", "m_hActiveWeapon"),
                "m_bDormant": get_field("CGameSceneNode", "m_bDormant"),
                "m_AttributeManager": get_field("C_EconEntity", "m_AttributeManager"),
                "m_Item": get_field("C_AttributeContainer", "m_Item"),
                "m_iItemDefinitionIndex": get_field("C_EconItemView", "m_iItemDefinitionIndex"),
                "m_pBoneArray": 496
            }

            missing_keys = [k for k, v in extracted_offsets.items() if v is None]
            if missing_keys:
                logger.error(f"Offset initialization error: Missing top-level keys {missing_keys}")
                return None

            return extracted_offsets

        except KeyError as e:
            logger.error(f"Offset initialization error: Missing key {e}")
            return None
        
    @staticmethod
    def get_color_name_from_hex(hex_color: str) -> str:
        """Get color name from hex value."""
        for name, hex_code in COLOR_CHOICES.items():
            if hex_code == hex_color:
                return name
        return "Black"
    
    @staticmethod
    def transliterate(text: str) -> str:
        """Converts Cyrillic characters in the given text to their Latin equivalents."""
        mapping = {
            'А': 'A',  'а': 'a',
            'Б': 'B',  'б': 'b',
            'В': 'V',  'в': 'v',
            'Г': 'G',  'г': 'g',
            'Д': 'D',  'д': 'd',
            'Е': 'E',  'е': 'e',
            'Ё': 'Yo', 'ё': 'yo',
            'Ж': 'Zh', 'ж': 'zh',
            'З': 'Z',  'з': 'z',
            'И': 'I',  'и': 'i',
            'Й': 'I',  'й': 'i',
            'К': 'K',  'к': 'k',
            'Л': 'L',  'л': 'l',
            'М': 'M',  'м': 'm',
            'Н': 'N',  'н': 'n',
            'О': 'O',  'о': 'o',
            'П': 'P',  'п': 'p',
            'Р': 'R',  'р': 'r',
            'С': 'S',  'с': 's',
            'Т': 'T',  'т': 't',
            'У': 'U',  'у': 'u',
            'Ф': 'F',  'ф': 'f',
            'Х': 'Kh', 'х': 'kh',
            'Ц': 'Ts', 'ц': 'ts',
            'Ч': 'Ch', 'ч': 'ch',
            'Ш': 'Sh', 'ш': 'sh',
            'Щ': 'Shch', 'щ': 'shch',
            'Ъ': '',   'ъ': '',
            'Ы': 'Y',  'ы': 'y',
            'Ь': '',   'ь': '',
            'Э': 'E',  'э': 'e',
            'Ю': 'Yu', 'ю': 'yu',
            'Я': 'Ya', 'я': 'ya'
        }
        return "".join(mapping.get(char, char) for char in text)

    @staticmethod
    def get_vk_code(key: str) -> int:
        """Convert a key string to its corresponding virtual key code."""
        key = key.lower()
        vk_codes = {
            # Mouse buttons
            "mouse1": 0x01,        # Left mouse button
            "mouse2": 0x02,        # Right mouse button
            "mouse3": 0x04,        # Middle mouse button
            "mouse4": 0x05,        # X1 mouse button
            "mouse5": 0x06,        # X2 mouse button
            # Common keyboard keys
            "space": 0x20,         # Spacebar
            "enter": 0x0D,         # Enter key
            "shift": 0x10,         # Shift key
            "ctrl": 0x11,          # Control key
            "alt": 0x12,           # Alt key
            "tab": 0x09,           # Tab key
            "backspace": 0x08,     # Backspace key
            "esc": 0x1B,           # Escape key
            # Alphabet keys
            "a": 0x41, "b": 0x42, "c": 0x43, "d": 0x44, "e": 0x45, "f": 0x46,
            "g": 0x47, "h": 0x48, "i": 0x49, "j": 0x4A, "k": 0x4B, "l": 0x4C,
            "m": 0x4D, "n": 0x4E, "o": 0x4F, "p": 0x50, "q": 0x51, "r": 0x52,
            "s": 0x53, "t": 0x54, "u": 0x55, "v": 0x56, "w": 0x57, "x": 0x58,
            "y": 0x59, "z": 0x5A,
            # Number keys
            "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
            "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
            # Function keys
            "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74,
            "f6": 0x75, "f7": 0x76, "f8": 0x77, "f9": 0x78, "f10": 0x79,
            "f11": 0x7A, "f12": 0x7B
        }
        return vk_codes.get(key, 0x20)  # Default to space key
