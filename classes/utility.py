from requests import get
from classes.logger import Logger

# Get a logger instance to log messages consistently throughout the application.
logger = Logger.get_logger()

class Utility:
    # Base URL for fetching game data files
    BASE_URL = "https://raw.githubusercontent.com/a2x/cs2-dumper/main/output"

    @staticmethod
    def fetch_offsets():
        """
        Fetches and parses game offset data from remote JSON files.
        
        Returns:
            tuple: (offset data, client data) if successful, otherwise (None, None).
        """
        try:
            # Fetch both JSON files concurrently for better performance
            response_offset = get(f"{Utility.BASE_URL}/offsets.json")
            response_client = get(f"{Utility.BASE_URL}/client_dll.json")

            # Validate responses
            if not Utility._validate_responses(response_offset, response_client):
                return None, None

            # Parse and return JSON data
            return response_offset.json(), response_client.json()

        except Exception as e:
            logger.error(f"Failed to fetch offsets: {e}")
            return None, None

    @staticmethod 
    def _validate_responses(*responses):
        """
        Helper method to validate HTTP responses.
        Returns True if all responses have 200 status code.
        """
        for response in responses:
            if response.status_code != 200:
                logger.error("Failed to fetch offsets from server.")
                return False
        return True
