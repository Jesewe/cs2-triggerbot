import threading
import time
import ctypes
from typing import Optional

from classes.config_manager import ConfigManager
from classes.memory_manager import MemoryManager
from classes.logger import Logger
from classes.utility import Utility

# Initialize the logger for consistent logging
logger = Logger.get_logger()
# Define the main loop sleep time for reduced CPU usage
MAIN_LOOP_SLEEP = 0.05
# Constants for bunnyhop
FORCE_JUMP_ACTIVE = 65537
FORCE_JUMP_INACTIVE = 256
KEY_SPACE = 0x20

class CS2Bunnyhop:
    """Manages the Bunnyhop functionality for Counter-Strike 2."""
    def __init__(self, offsets: dict, client_data: dict, buttons_data: dict) -> None:
        """
        Initialize the Bunnyhop with offsets, client data, and buttons data.
        """
        # Load the configuration settings
        self.config = ConfigManager.load_config()
        self.memory_manager = MemoryManager(offsets, client_data, buttons_data)
        self.memory_manager.config = self.config  # Pass configuration to MemoryManager
        self.is_running = False
        self.stop_event = threading.Event()
        self.force_jump_address: Optional[int] = None

    def initialize_force_jump(self) -> bool:
        """Initialize the force jump address."""
        if self.memory_manager.dwForceJump is None:
            logger.error("dwForceJump offset not initialized.")
            return False
        try:
            self.force_jump_address = self.memory_manager.client_base + self.memory_manager.dwForceJump
            logger.info(f"Force jump address set to {hex(self.force_jump_address)}")
            return True
        except Exception as e:
            logger.error(f"Error setting force jump address: {e}")
            return False

    def perform_jump(self, is_jumping: bool) -> bool:
        """Perform a single jump action."""
        try:
            if not is_jumping:
                time.sleep(0.01)
                self.memory_manager.write_int(self.force_jump_address, FORCE_JUMP_ACTIVE)
                return True
            else:
                time.sleep(0.01)
                self.memory_manager.write_int(self.force_jump_address, FORCE_JUMP_INACTIVE)
                return False
        except Exception as e:
            logger.error(f"Error performing jump: {e}")
            return is_jumping

    def start(self) -> None:
        """Start the Bunnyhop."""
        if not self.memory_manager.initialize():
            logger.error("Failed to initialize memory manager.")
            return
        if not self.initialize_force_jump():
            logger.error("Failed to initialize force jump address.")
            return

        self.is_running = True
        logger.info("Bunnyhop started.")

        is_game_active = Utility.is_game_active
        sleep = time.sleep
        is_jumping = False

        while not self.stop_event.is_set():
            try:
                if not is_game_active():
                    sleep(MAIN_LOOP_SLEEP)
                    continue

                if ctypes.windll.user32.GetAsyncKeyState(KEY_SPACE) & 0x8000:
                    is_jumping = self.perform_jump(is_jumping)

                sleep(MAIN_LOOP_SLEEP)
            except KeyboardInterrupt:
                logger.info("Bunnyhop stopped by user.")
                self.stop()
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
                sleep(MAIN_LOOP_SLEEP)

    def stop(self) -> None:
        """Stop the Bunnyhop and clean up resources."""
        self.is_running = False
        self.stop_event.set()
        logger.info("Bunnyhop stopped.")