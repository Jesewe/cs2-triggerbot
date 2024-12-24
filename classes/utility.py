import os, json, requests

from classes.logger import Logger

# Get a logger instance to log messages consistently throughout the application.
logger = Logger.get_logger()

class Utility:
    @staticmethod
    def fetch_offsets():
        """
        Fetches JSON data from two remote URLs and parses it.
        - Retrieves data from 'offsets.json' and 'client_dll.json' on GitHub.
        - Logs an error if either request fails or the server returns a non-200 status code.
        - Handles exceptions gracefully, ensuring no unhandled errors crash the application.
        
        Returns:
            tuple: (offset data, client data) if successful, otherwise (None, None).
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