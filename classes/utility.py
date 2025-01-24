import os, json, requests, psutil, sys
import pygetwindow as gw

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

            # Check if the requests were successful
            if response_offset.status_code != 200:
                # Log an error if the offsets request fails
                logger.error("Failed to fetch offsets from server: offsets.json request failed.")
                return None, None

            if response_client.status_code != 200:
                # Log an error if the client DLL request fails
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
        
    @staticmethod
    def check_for_updates(current_version):
        """
        Checks the GitHub repository for the latest version of the software.
        Compares the current version with the latest version and returns the update URL if an update is available.
        """
        try:
            # Fetch the latest release data from the GitHub API
            response = requests.get("https://api.github.com/repos/Jesewe/cs2-triggerbot/releases/latest")
            response.raise_for_status()

            # Parse the JSON response and extract the latest version and release URL
            latest_release = response.json()
            latest_version = latest_release["tag_name"]
            update_url = latest_release["html_url"]

            if version.parse(latest_version) > version.parse(current_version):
                # Log that a new update is available
                logger.info(f"New version available: {latest_version}.")
                return update_url
            else:
                # Log that no updates are available
                logger.info("No new updates available.")
                return None
        except requests.exceptions.RequestException as e:
            # Log the request exception details if any errors occur during the process
            logger.error(f"Update check failed: {e}")
            return None
        except Exception as e:
            # Log any other exceptions that may occur
            logger.error(f"An unexpected error occurred during update check: {e}")
            return None

    @staticmethod
    def fetch_last_offset_update(last_update_label):
        """
        Fetches the timestamp of the latest commit to the offsets repository.
        Updates the UI label with the timestamp or an error message if the fetch fails.
        """
        try:
            # Fetch the latest commit data from the GitHub API
            response = requests.get("https://api.github.com/repos/a2x/cs2-dumper/commits/main")
            response.raise_for_status()

            # Parse the commit data and extract the timestamp
            commit_data = response.json()
            commit_timestamp = commit_data["commit"]["committer"]["date"]

            # Parse and format the timestamp
            last_update_dt = parse_date(commit_timestamp)
            formatted_timestamp = last_update_dt.strftime("%m/%d/%Y %H:%M:%S")
            
            # Update the label
            last_update_label.setText(f"Last offsets update: {formatted_timestamp} (UTC)")
            last_update_label.setStyleSheet("color: #ffa420; font-weight: bold;")
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                # Handle rate limit exceeded error
                last_update_label.setText("Request limit exceeded. Please try again later.")
                last_update_label.setStyleSheet("color: #0bda51; font-weight: bold;")
                logger.error(f"Offset update fetch failed: {e} (403 Forbidden)")
            else:
                # Handle other HTTP errors
                last_update_label.setText("Error fetching last offsets update. Please check your internet connection or try again later.")
                last_update_label.setStyleSheet("color: #0bda51; font-weight: bold;")
                logger.error(f"Offset update fetch failed: {e}")
        except Exception as e:
            # Handle other exceptions
            last_update_label.setText("Error fetching last offsets update. Please check your internet connection or try again later.")
            last_update_label.setStyleSheet("color: #0bda51; font-weight: bold;")
            logger.error(f"Offset update fetch failed: {e}")

    @staticmethod
    def resource_path(relative_path):
        """Returns the path to a resource that supports both normal startup and startup from .exe."""
        if hasattr(sys, '_MEIPASS'):
            # If the application is frozen, use the MEIPASS path
            return os.path.join(sys._MEIPASS, relative_path)
        # If the application is not frozen, use the relative path
        return os.path.join(os.path.abspath("."), relative_path)

    @staticmethod
    def is_game_active():
        """Check if the game window is active using the 'pygetwindow' module."""
        windows = gw.getWindowsWithTitle('Counter-Strike 2')
        return any(window.isActive for window in windows)

    @staticmethod
    def is_game_running():
        """Check if the game process is running."""
        return any(proc.info['name'] == 'cs2.exe' for proc in psutil.process_iter(attrs=['name']))