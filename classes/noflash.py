import threading
import time
from typing import Optional

from classes.config_manager import ConfigManager
from classes.memory_manager import MemoryManager
from classes.logger import Logger
from classes.utility import Utility

# Initialize the logger for consistent logging
logger = Logger.get_logger()
# Define the main loop sleep time for NoFlash
NOFLASH_LOOP_SLEEP = 0.1

class CS2NoFlash:
    """Manages the NoFlash functionality for Counter-Strike 2."""
    def __init__(self, memory_manager: MemoryManager) -> None:
        """
        Initialize the NoFlash with a shared MemoryManager instance.
        """
        # Load the configuration settings
        self.config = ConfigManager.load_config()
        self.memory_manager = memory_manager
        self.is_running = False
        self.stop_event = threading.Event()
        self.local_player_address: Optional[int] = None

    def update_config(self, config):
        """Update the configuration settings."""
        self.config = config
        logger.debug("NoFlash configuration updated.")

    def initialize_local_player(self) -> bool:
        """Initialize the local player address."""
        if self.memory_manager.dwLocalPlayerPawn is None or self.memory_manager.m_flFlashDuration is None:
            logger.error("dwLocalPlayerPawn or m_flFlashDuration offset not initialized.")
            return False
        try:
            self.local_player_address = self.memory_manager.client_base + self.memory_manager.dwLocalPlayerPawn
            return True
        except Exception as e:
            logger.error(f"Error setting local player address: {e}")
            return False

    def disable_flash(self) -> None:
        """Set the flash duration to 0.0."""
        try:
            player_position = self.memory_manager.read_longlong(self.local_player_address)
            if player_position:
                self.memory_manager.write_float(player_position + self.memory_manager.m_flFlashDuration, 0.0)
        except Exception as e:
            logger.error(f"Error disabling flash: {e}")

    def start(self) -> None:
        """Start the NoFlash."""
        if not self.initialize_local_player():
            logger.error("Failed to initialize local player address.")
            return

        self.is_running = True

        is_game_active = Utility.is_game_active
        sleep = time.sleep

        while not self.stop_event.is_set():
            try:
                if not is_game_active():
                    sleep(NOFLASH_LOOP_SLEEP)
                    continue

                self.disable_flash()
                sleep(NOFLASH_LOOP_SLEEP)
            except KeyboardInterrupt:
                logger.debug("NoFlash stopped by user.")
                self.stop()
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                sleep(NOFLASH_LOOP_SLEEP)

    def stop(self) -> None:
        """Stop the NoFlash and clean up resources."""
        self.is_running = False
        self.stop_event.set()
        
        logger.debug("NoFlash stopped.")