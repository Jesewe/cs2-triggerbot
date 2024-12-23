import os, json

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
    CONFIG_FILE = os.path.join(CONFIG_DIRECTORY, 'config.json')

    # Default configuration settings
    DEFAULT_CONFIG = {
        "Settings": {
            "TriggerKey": "x",  # Default trigger key
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
        # Return cached configuration if available
        if cls._config_cache is not None:
            return cls._config_cache

        # Ensure the configuration directory exists
        if not os.path.exists(cls.CONFIG_DIRECTORY):
            os.makedirs(cls.CONFIG_DIRECTORY)

        # Check if the configuration file exists
        if not os.path.exists(cls.CONFIG_FILE):
            # If not, create the configuration file with default settings
            logger.info(f"config.json not found at {cls.CONFIG_FILE}, creating a default configuration.")
            cls.save_config(cls.DEFAULT_CONFIG, log_info=False)
            cls._config_cache = cls.DEFAULT_CONFIG
        else:
            try:
                # Attempt to read and parse the configuration file
                with open(cls.CONFIG_FILE, 'r') as config_file:
                    cls._config_cache = json.load(config_file)
                    logger.info("Loaded configuration.")
            except (json.JSONDecodeError, IOError) as e:
                # Handle errors during configuration loading
                logger.exception(f"Failed to load configuration: {e}")
                cls.save_config(cls.DEFAULT_CONFIG, log_info=False)
                cls._config_cache = cls.DEFAULT_CONFIG

        return cls._config_cache

    @classmethod
    def save_config(cls, config, log_info=True):
        """
        Saves the configuration to the configuration file.
        Updates the cache with the new configuration.

        Args:
            config (dict): The configuration settings to save.
            log_info (bool): Whether to log a success message after saving.
        """
        cls._config_cache = config
        try:
            # Write the configuration to the file without pretty formatting for better performance
            with open(cls.CONFIG_FILE, 'w') as config_file:
                json.dump(config, config_file)
                if log_info:
                    logger.info(f"Saved configuration to {cls.CONFIG_FILE}.")
        except IOError as e:
            # Log errors that occur during the save process
            logger.exception(f"Failed to save configuration: {e}")