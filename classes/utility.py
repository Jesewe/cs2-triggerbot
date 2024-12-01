from requests import get
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
            response_offset = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json")
            # Fetch the client DLL JSON from the second URL
            response_client = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json")

            # Check if both requests were successful (HTTP 200 status)
            if response_offset.status_code != 200 or response_client.status_code != 200:
                # Log an error if either request fails
                logger.error("Failed to fetch offsets from server.")
                return None, None

            # Parse the responses as JSON
            offset = response_offset.json()
            client = response_client.json()

            # Return the parsed JSON objects
            return offset, client

        except Exception as e:
            # Log the exception details if any errors occur during the process
            logger.error(f"Failed to fetch offsets: {e}")
            return None, None