import os, json, requests, psutil, win32gui

from packaging import version
from dateutil.parser import parse as parse_date

from classes.logger import Logger

# Initialize the logger for consistent logging
logger = Logger.get_logger()

class Utility:
    @staticmethod
    def fetch_offsets():
        """
        Fetches JSON data from two remote URLs and parses it.
        - Retrieves data from 'offsets.json' and 'client_dll.json' on GitHub.
        - Logs an error if either request fails or the server returns a non-200 status code.
        - Handles exceptions gracefully, ensuring no unhandled errors crash the application.
        """
        try:
            # Fetch the offsets JSON from the first URL
            offsets_url = os.getenv('OFFSETS_URL', 'https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json')
            response_offset = requests.get(offsets_url)
            # Fetch the client DLL JSON from the second URL
            client_dll_url = os.getenv('CLIENT_DLL_URL', 'https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json')
            response_client = requests.get(client_dll_url)

            # Check if both requests were successful (HTTP 200 status)
            if response_offset.status_code != 200:
                logger.error("Failed to fetch offsets from server: offsets.json request failed.")
                return None, None

            if response_client.status_code != 200:
                logger.error("Failed to fetch offsets from server: client_dll.json request failed.")
                return None, None

            try:
                # Parse the responses as JSON
                offset = response_offset.json()
                client = response_client.json()

                # Return the parsed JSON objects
                return offset, client
            except json.JSONDecodeError as e:
                # Log the JSON decode error
                logger.error(f"Failed to decode JSON response from {response_offset.url if response_offset.status_code != 200 else response_client.url}: {e}")
                return None, None

        except requests.exceptions.RequestException as e:
            # Log the request exception details if any errors occur during the process
            logger.error(f"Request failed: {e}")
            return None, None
        except json.JSONDecodeError as e:
            # Log the JSON decode error
            logger.error(f"Failed to decode JSON response: {e}")
            return None, None
        except Exception as e:
            # Log any other exceptions that may occur
            logger.exception(f"An unexpected error occurred: {e}")
            return None, None
        
    def check_for_updates(current_version, update_info):
        """
        Checks the GitHub repository for the latest version of the software.
        Compares the current version with the latest version and updates the UI accordingly.
        """
        try:
            response = requests.get("https://api.github.com/repos/Jesewe/cs2-triggerbot/tags")
            response.raise_for_status()
            latest_version = response.json()[0]["name"]

            if version.parse(latest_version) > version.parse(current_version):
                update_info.setText(f"New version available: {latest_version}. Please update for the latest fixes and features.")
                update_info.setStyleSheet("color: #BB86FC;")
            elif version.parse(current_version) > version.parse(latest_version):
                update_info.setText("Developer version: You are using a pre-release or developer version.")
                update_info.setStyleSheet("color: #F1C40F;")
            else:
                update_info.setText("You are using the latest version.")
                update_info.setStyleSheet("color: #df73ff;")
        except Exception as e:
            update_info.setText(f"Error checking for updates. {e}")
            update_info.setStyleSheet("color: red;")

    def fetch_last_offset_update(last_update_label):
        """
        Fetches the timestamp of the latest commit to the offsets repository.
        Updates the UI label with the timestamp or an error message if the fetch fails.
        """
        try:
            response = requests.get("https://api.github.com/repos/a2x/cs2-dumper/commits/main")
            response.raise_for_status()
            commit_data = response.json()
            commit_timestamp = commit_data["commit"]["committer"]["date"]

            # Parse and format the timestamp
            last_update_dt = parse_date(commit_timestamp)
            formatted_timestamp = last_update_dt.strftime("%m/%d/%Y %H:%M:%S")
            
            # Update the label
            last_update_label.setText(f"Last offsets update: {formatted_timestamp} (UTC)")
            last_update_label.setStyleSheet("color: orange; font-weight: bold;")
        except Exception as e:
            last_update_label.setText("Error fetching last offsets update. Please check your internet connection or try again later.")
            last_update_label.setStyleSheet("color: orange; font-weight: bold;")
            logger.error(f"Offset update fetch failed: {e}")

    @staticmethod
    def is_game_active():
        """Check if the game window is active."""
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd) == "Counter-Strike 2"

    @staticmethod
    def is_game_running():
        """Check if the game process is running."""
        return any(proc.info['name'] == 'cs2.exe' for proc in psutil.process_iter(attrs=['name']))