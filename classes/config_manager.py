import os, json
from pathlib import Path

from classes.logger import Logger

# Initialize the logger for consistent logging
logger = Logger.get_logger()

class ConfigManager:
    """
    Manages the configuration file for the application.
    Provides methods to load and save configuration settings, 
    with caching for efficiency and default configuration management.
    """
    # Directory where the configuration file is stored
    CONFIG_DIRECTORY = os.path.expanduser(r'~\AppData\Local\Requests\ItsJesewe')
    # Full path to the configuration file
    CONFIG_FILE = Path(CONFIG_DIRECTORY) / 'config.json'

    # Default configuration settings
    DEFAULT_CONFIG = {
        "Settings": {
            "TriggerKey": "x",  # Default trigger key
            "ToggleMode": False, # Whether to use toggle mode for the trigger
            "ShotDelayMin": 0.01,  # Minimum delay between shots in seconds
            "ShotDelayMax": 0.03,  # Maximum delay between shots in seconds
            "AttackOnTeammates": False,  # Whether to attack teammates
            "PostShotDelay": 0.1  # Delay after each shot
        }
    }

    # Cache to store the loaded configuration
    _config_cache = None

    @classmethod
    def load_config(cls):
        """
        Loads the configuration from the configuration file.
        - Creates the configuration directory and file with default settings if they do not exist.
        - Caches the configuration to avoid redundant file reads.
        Returns:
            dict: The configuration settings.
        """
        # Return cached configuration if available.
        if cls._config_cache is not None:
            return cls._config_cache

        # Ensure the configuration directory exists.
        os.makedirs(cls.CONFIG_DIRECTORY, exist_ok=True)

        # Create the configuration file with default settings if it doesn't exist.
        if not Path(cls.CONFIG_FILE).exists():
            logger.info("config.json not found at %s, creating a default configuration.", cls.CONFIG_FILE)
            cls.save_config(cls.DEFAULT_CONFIG, log_info=False)
            cls._config_cache = cls.DEFAULT_CONFIG
        else:
            try:
                # Read and parse the configuration file.
                cls._config_cache = json.loads(Path(cls.CONFIG_FILE).read_text())
                logger.info("Loaded configuration.")
            except (json.JSONDecodeError, IOError) as e:
                logger.exception("Failed to load configuration: %s", e)
                cls.save_config(cls.DEFAULT_CONFIG, log_info=False)
                cls._config_cache = cls.DEFAULT_CONFIG.copy()

            # Update the configuration if any keys are missing.
            if cls._update_config(cls.DEFAULT_CONFIG, cls._config_cache):
                cls.save_config(cls._config_cache, log_info=False)
        return cls._config_cache

    @classmethod
    def _update_config(cls, default: dict, current: dict) -> bool:
        """
        Recursively update `current` with missing keys from `default`.
        Returns True if any keys were added.
        """
        updated = False
        for key, value in default.items():
            if key not in current:
                current[key] = value
                updated = True
            elif isinstance(value, dict) and isinstance(current.get(key), dict):
                if cls._update_config(value, current[key]):
                    updated = True
        return updated

    @classmethod
    def save_config(cls, config: dict, log_info: bool = True):
        """
        Saves the configuration to the configuration file.
        Updates the cache with the new configuration.
        Args:
            config (dict): The configuration settings to save.
            log_info (bool): Whether to log a success message after saving.
        """
        cls._config_cache = config
        try:
            # Ensure the configuration directory exists.
            Path(cls.CONFIG_DIRECTORY).mkdir(parents=True, exist_ok=True)
            # Write the configuration to the file with pretty formatting for readability.
            Path(cls.CONFIG_FILE).write_text(json.dumps(config, indent=4))
            if log_info:
                logger.info("Saved configuration to %s.", cls.CONFIG_FILE)
        except IOError as e:
            logger.exception("Failed to save configuration: %s", e)