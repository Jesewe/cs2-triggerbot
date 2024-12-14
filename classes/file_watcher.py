from watchdog.events import FileSystemEventHandler
from classes.config_manager import ConfigManager
from classes.logger import Logger

# Get logger instance for the module
logger = Logger.get_logger()

class ConfigFileChangeHandler(FileSystemEventHandler):
    """
    A file system event handler for monitoring changes to the configuration file.
    Automatically updates the bot's configuration when the configuration file is modified.
    """
    def __init__(self, bot):
        """
        Initializes the file change handler with a reference to the bot instance.
        
        Args:
            bot: Reference to the bot instance to update configuration
        """
        super().__init__()
        self._bot = bot  # Use protected naming convention for instance variable

    def on_modified(self, event):
        """
        Handles file modification events by reloading config if the config file changed.
        
        Args:
            event: FileSystemEvent containing the modified file information
        """
        # Only process events for the config file
        if event.src_path != ConfigManager.CONFIG_FILE:
            return
            
        try:
            # Load and apply new configuration
            self._bot.update_config(ConfigManager.load_config())
            logger.info("Configuration file updated and applied successfully.")
        except Exception as e:
            # Log detailed error information
            logger.error(f"Failed to reload configuration. Error: {str(e)}")
