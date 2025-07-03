import os, orjson
from pathlib import Path
from pyMeow import get_color, fade_color

from classes.logger import Logger

# Initialize the logger for consistent logging
logger = Logger.get_logger()

class ConfigManager:
    """
    Manages the configuration file for the application.
    Provides methods to load and save configuration settings, 
    with caching for efficiency and default configuration management.
    """
    # Application version
    VERSION = "v1.2.5.1"
    # Directory where the update files are stored
    UPDATE_DIRECTORY = os.path.expanduser(r'~\AppData\Local\Requests\ItsJesewe\Update')
    # Directory where the configuration file is stored
    CONFIG_DIRECTORY = os.path.expanduser(r'~\AppData\Local\Requests\ItsJesewe')
    # Full path to the configuration file
    CONFIG_FILE = Path(CONFIG_DIRECTORY) / 'config.json'

    # Default configuration settings with General, Trigger, and Overlay categories
    DEFAULT_CONFIG = {
        "General": {
            "Trigger": False,                    # Enable or disable the trigger feature
            "Overlay": False,                    # Enable or disable the overlay feature
            "Bunnyhop": False,                   # Enable or disable the bunnyhop feature
            "Noflash": False                     # Enable or disable the noflash feature
        },
        "Trigger": {
            "TriggerKey": "x",                   # Key to activate the trigger
            "ToggleMode": False,                 # Enable toggle mode for the trigger
            "ShotDelayMin": 0.01,                # Minimum delay between shots
            "ShotDelayMax": 0.03,                # Maximum delay between shots
            "AttackOnTeammates": False,          # Allow attacking teammates
            "PostShotDelay": 0.1                 # Delay after shooting before the next action
        },
        "Overlay": {
            "enable_box": True,                  # Enable or disable the bounding box overlay
            "draw_snaplines": True,              # Enable or disable snaplines in the overlay
            "snaplines_color_hex": "#FFFFFF",  # Color of the snaplines in hexadecimal format
            "box_line_thickness": 1.0,           # Thickness of the bounding box lines
            "box_color_hex": "#FFA500",        # Color of the bounding box in hexadecimal format
            "text_color_hex": "#FFFFFF",       # Color of the text in the overlay
            "draw_health_numbers": True,         # Enable or disable health numbers in the overlay
            "use_transliteration": False,        # Use transliteration for names in the overlay
            "draw_nicknames": True,              # Enable or disable drawing nicknames in the overlay
            "draw_teammates": True,              # Enable or disable drawing teammates in the overlay
            "teammate_color_hex": "#00FFFF",   # Color for teammates in the overlay
            "enable_minimap": False,             # Enable or disable the minimap overlay
            "minimap_size": 200                  # Size of the minimap in pixels
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
        """
        # Return cached configuration if available.
        if cls._config_cache is not None:
            return cls._config_cache

        # Ensure the configuration directory exists.
        os.makedirs(cls.CONFIG_DIRECTORY, exist_ok=True)

        if not Path(cls.CONFIG_FILE).exists():
            logger.info("config.json not found at %s, creating a default configuration.", cls.CONFIG_FILE)
            cls.save_config(cls.DEFAULT_CONFIG, log_info=False)
            cls._config_cache = cls.DEFAULT_CONFIG
        else:
            try:
                # Read and parse the configuration file using orjson.
                file_bytes = Path(cls.CONFIG_FILE).read_bytes()
                cls._config_cache = orjson.loads(file_bytes)
                logger.info("Loaded configuration.")
            except (orjson.JSONDecodeError, IOError) as e:
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
        """
        cls._config_cache = config
        try:
            # Ensure the configuration directory exists.
            Path(cls.CONFIG_DIRECTORY).mkdir(parents=True, exist_ok=True)
            # Serialize and write the configuration to the file with pretty formatting.
            config_bytes = orjson.dumps(config, option=orjson.OPT_INDENT_2)
            Path(cls.CONFIG_FILE).write_bytes(config_bytes)
            if log_info:
                logger.info("Saved configuration to %s.", cls.CONFIG_FILE)
        except IOError as e:
            logger.exception("Failed to save configuration: %s", e)

COLOR_CHOICES = {
    "Orange": "#FFA500",
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Blue": "#0000FF",
    "White": "#FFFFFF",
    "Black": "#000000",
    "Cyan": "#00FFFF",
    "Yellow": "#FFFF00"
}

class Colors:
    orange = get_color("orange")
    black = get_color("black")
    cyan = get_color("cyan")
    white = get_color("white")
    grey = fade_color(get_color("#242625"), 0.7)
    red = get_color("red")
    green = get_color("green")
    blue = get_color("blue")
    yellow = get_color("yellow")