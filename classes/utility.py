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
        """Checks GitHub for the latest version and returns the download URL of 'VioletWing.exe' if an update is available."""
        try:
            response = requests.get("https://api.github.com/repos/Jesewe/VioletWing/releases/latest")
            response.raise_for_status()
            data = orjson.loads(response.content)
            latest_version = data.get("tag_name")
            if version.parse(latest_version) > version.parse(current_version):
                for asset in data.get("assets", []):
                    if asset.get("name") == "VioletWing.exe":
                        download_url = asset.get("browser_download_url")
                        if download_url:
                            logger.info(f"New version available: {latest_version}.")
                            return download_url
                logger.warning("No 'VioletWing.exe' found in the latest release assets.")
                return None
            logger.info("No new updates available.")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Update check failed: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during update check: {e}")
            return None

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
            client = offsets["client.dll"]
            dwEntityList = client["dwEntityList"]
            dwLocalPlayerPawn = client["dwLocalPlayerPawn"]
            dwLocalPlayerController = client["dwLocalPlayerController"]
            dwViewMatrix = client["dwViewMatrix"]
            dwForceJump = buttons_data["client.dll"]["jump"]

            classes = client_data["client.dll"]["classes"]
            m_iHealth = classes["C_BaseEntity"]["fields"]["m_iHealth"]
            m_iTeamNum = classes["C_BaseEntity"]["fields"]["m_iTeamNum"]
            m_iIDEntIndex = classes["C_CSPlayerPawnBase"]["fields"]["m_iIDEntIndex"]
            m_iszPlayerName = classes["CBasePlayerController"]["fields"]["m_iszPlayerName"]
            m_vOldOrigin = classes["C_BasePlayerPawn"]["fields"]["m_vOldOrigin"]
            m_pGameSceneNode = classes["C_BaseEntity"]["fields"]["m_pGameSceneNode"]
            m_bDormant = classes["CGameSceneNode"]["fields"]["m_bDormant"]
            m_hPlayerPawn = classes["CCSPlayerController"]["fields"]["m_hPlayerPawn"]
            m_flFlashDuration = classes["C_CSPlayerPawnBase"]["fields"]["m_flFlashDuration"]
            m_pBoneArray = 496  # Default value

            return {
                "dwEntityList": dwEntityList,
                "dwLocalPlayerPawn": dwLocalPlayerPawn,
                "dwLocalPlayerController": dwLocalPlayerController,
                "dwViewMatrix": dwViewMatrix,
                "dwForceJump": dwForceJump,
                "m_iHealth": m_iHealth,
                "m_iTeamNum": m_iTeamNum,
                "m_iIDEntIndex": m_iIDEntIndex,
                "m_iszPlayerName": m_iszPlayerName,
                "m_vOldOrigin": m_vOldOrigin,
                "m_pGameSceneNode": m_pGameSceneNode,
                "m_bDormant": m_bDormant,
                "m_hPlayerPawn": m_hPlayerPawn,
                "m_flFlashDuration": m_flFlashDuration,
                "m_pBoneArray": m_pBoneArray
            }
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