import os
import json
from classes.logger import Logger

# Get logger instance for the module
logger = Logger.get_logger()

class ConfigManager:
    """
    Manages application configuration file operations including loading, saving and caching.
    Handles default configuration and error cases.
    """
    # Configuration file paths
    CONFIG_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe')
    CONFIG_FILE = os.path.join(CONFIG_DIRECTORY, 'config.json')

    # Default configuration with gameplay settings
    DEFAULT_CONFIG = {
        "Settings": {
            "TriggerKey": "x",
            "ShotDelayMin": 0.01,
            "ShotDelayMax": 0.03, 
            "AttackOnTeammates": False,
            "PostShotDelay": 0.1
        }
    }

    # Cache for loaded configuration
    _config_cache = None

    @classmethod
    def load_config(cls):
        """
        Loads and caches configuration from file, creating defaults if needed.
        
        Returns:
            dict: Current configuration settings
        """
        # Return cached config if available
        if cls._config_cache:
            return cls._config_cache

        # Create config directory if missing
        os.makedirs(cls.CONFIG_DIRECTORY, exist_ok=True)

        # Handle missing config file
        if not os.path.exists(cls.CONFIG_FILE):
            logger.info("Creating default configuration file")
            cls.save_config(cls.DEFAULT_CONFIG, log_info=False)
            return cls.DEFAULT_CONFIG

        try:
            # Load and parse config file
            with open(cls.CONFIG_FILE, 'r') as f:
                cls._config_cache = json.load(f)
                logger.info("Configuration loaded successfully")
                return cls._config_cache

        except (json.JSONDecodeError, IOError) as e:
            # Return defaults on load failure
            logger.error(f"Configuration load failed: {e}")
            return cls.DEFAULT_CONFIG

    @classmethod 
    def save_config(cls, config, log_info=True):
        """
        Saves configuration to file and updates cache.

        Args:
            config (dict): Configuration to save
            log_info (bool): Whether to log success message
        """
        cls._config_cache = config
        try:
            # Write formatted config to file
            with open(cls.CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
                if log_info:
                    logger.info("Configuration saved successfully")
        except IOError as e:
            logger.error(f"Configuration save failed: {e}")
