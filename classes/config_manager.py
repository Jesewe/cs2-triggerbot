import os
import json
from classes.logger import Logger

logger = Logger.get_logger()

class ConfigManager:
    CONFIG_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe')
    CONFIG_FILE = os.path.join(CONFIG_DIRECTORY, 'config.json')

    DEFAULT_CONFIG = {
        "Settings": {
            "TriggerKey": "x",
            "ShotDelayMin": 0.01,
            "ShotDelayMax": 0.03,
            "AttackOnTeammates": False,
            "PostShotDelay": 0.1
        }
    }

    _config_cache = None

    @classmethod
    def load_config(cls):
        if cls._config_cache is not None:
            return cls._config_cache

        if not os.path.exists(cls.CONFIG_DIRECTORY):
            os.makedirs(cls.CONFIG_DIRECTORY)

        if not os.path.exists(cls.CONFIG_FILE):
            logger.info("config.json not found, creating a default configuration.")
            cls.save_config(cls.DEFAULT_CONFIG, log_info=False)
            cls._config_cache = cls.DEFAULT_CONFIG
        else:
            try:
                with open(cls.CONFIG_FILE, 'r') as config_file:
                    cls._config_cache = json.load(config_file)
                    logger.info("Loaded configuration.")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load configuration: {e}")
                cls._config_cache = cls.DEFAULT_CONFIG

        return cls._config_cache

    @classmethod
    def save_config(cls, config, log_info=True):
        cls._config_cache = config
        with open(cls.CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file, indent=4)
            if log_info:
                logger.info("Saved configuration.")