import os
import requests
import psutil
import sys
import subprocess
import pygetwindow as gw
import orjson
from packaging import version
from dateutil.parser import parse as parse_date

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

            if response_offset.status_code != 200:
                logger.error("Failed to fetch offsets: offsets.json request failed.")
                return None, None

            if response_client.status_code != 200:
                logger.error("Failed to fetch offsets: client_dll.json request failed.")
                return None, None

            try:
                offset = orjson.loads(response_offset.content)
                client = orjson.loads(response_client.content)
                return offset, client
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
        """Checks GitHub for the latest version and returns the download URL of 'CS2.Triggerbot.exe' if an update is available."""
        try:
            response = requests.get("https://api.github.com/repos/Jesewe/cs2-triggerbot/releases/latest")
            response.raise_for_status()
            data = orjson.loads(response.content)
            latest_version = data.get("tag_name")
            if version.parse(latest_version) > version.parse(current_version):
                for asset in data.get("assets", []):
                    if asset.get("name") == "CS2.Triggerbot.exe":
                        download_url = asset.get("browser_download_url")
                        if download_url:
                            logger.info(f"New version available: {latest_version}.")
                            return download_url
                logger.warning("No 'CS2.Triggerbot.exe' found in the latest release assets.")
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