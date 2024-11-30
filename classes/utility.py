from requests import get
from classes.logger import Logger

logger = Logger.get_logger()

class Utility:
    @staticmethod
    def fetch_offsets():
        try:
            response_offset = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json")
            response_client = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json")

            if response_offset.status_code != 200 or response_client.status_code != 200:
                logger.error("Failed to fetch offsets from server.")
                return None, None

            offset = response_offset.json()
            client = response_client.json()
            return offset, client
        except Exception as e:
            logger.error(f"Failed to fetch offsets: {e}")
            return None, None