from watchdog.events import FileSystemEventHandler
from classes.config_manager import ConfigManager
from classes.logger import Logger

# Initialize the logger for consistent logging
logger = Logger.get_logger()

class ConfigFileChangeHandler(FileSystemEventHandler):
    """
    A file system event handler for monitoring changes to the configuration file.
    Automatically updates the bot's configuration when the configuration file is modified.
    """
    def __init__(self, bot):
        """
        Initializes the file change handler with a reference to the bot instance.
        """
        self.bot = bot

    def on_modified(self, event):
        """
        Called when a file or directory is modified.
        """
        if event.src_path == ConfigManager.CONFIG_FILE:
            try:
                # Reload the updated configuration file
                new_config = ConfigManager.load_config()
                # Update the bot's configuration with the new settings
                self.bot.update_config(new_config)
                logger.info("Configuration file updated and applied successfully.")
            except Exception as e:
                # Log an error if the configuration update fails
                logger.error(f"Failed to reload configuration: {e}")