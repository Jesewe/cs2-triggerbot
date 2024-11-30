from watchdog.events import FileSystemEventHandler
from classes.config_manager import ConfigManager
from classes.logger import Logger

logger = Logger.get_logger()

class ConfigFileChangeHandler(FileSystemEventHandler):
    def __init__(self, bot):
        self.bot = bot

    def on_modified(self, event):
        if event.src_path == ConfigManager.CONFIG_FILE:
            try:
                new_config = ConfigManager.load_config()
                self.bot.update_config(new_config)
            except Exception as e:
                logger.error(f"Failed to reload configuration: {e}")