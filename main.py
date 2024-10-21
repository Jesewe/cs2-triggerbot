import pymem
import pymem.process
import time
import os
import ctypes
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
from random import uniform
import logging
from requests import get
from packaging import version
from colorama import init, Fore
import json
import keyboard

# Initialize colorama for colored console output
init(autoreset=True)

# Initialize mouse controller for trigger actions
mouse = Controller()

class Logger:
    """Handles logging setup for the application."""

    LOG_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe\crashes')
    LOG_FILE = os.path.join(LOG_DIRECTORY, 'tb_logs.log')

    @staticmethod
    def setup_logging():
        """Set up the logging configuration with the default log level INFO."""
        os.makedirs(Logger.LOG_DIRECTORY, exist_ok=True)
        with open(Logger.LOG_FILE, 'w') as f:
            pass
        
        logging.basicConfig(
            level=logging.INFO,  # Default to INFO level logging
            format='%(levelname)s: %(message)s',
            handlers=[logging.FileHandler(Logger.LOG_FILE), logging.StreamHandler()]
        )

class ConfigManager:
    """Handles loading, saving, and validating configuration settings."""
    
    CONFIG_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe')
    CONFIG_FILE = os.path.join(CONFIG_DIRECTORY, 'config.json')
    
    DEFAULT_CONFIG = {
        "Settings": {
            "TriggerKey": "x",  # KEY x by default
            "ShotDelayMin": 0.01,  # Minimum delay between shots
            "ShotDelayMax": 0.03,  # Maximum delay between shots
            "AttackOnTeammates": False  # Should the bot attack teammates?
        }
    }

    @staticmethod
    def load_config():
        """Loads the configuration from a JSON file, creating defaults if needed."""
        if not os.path.exists(ConfigManager.CONFIG_DIRECTORY):
            os.makedirs(ConfigManager.CONFIG_DIRECTORY)

        if not os.path.exists(ConfigManager.CONFIG_FILE):
            logging.info(f"{Fore.YELLOW}config.json not found, creating a default configuration.")
            ConfigManager.save_config(ConfigManager.DEFAULT_CONFIG)

        # Load the configuration from file
        try:
            with open(ConfigManager.CONFIG_FILE, 'r') as config_file:
                config = json.load(config_file)
                logging.info(f"{Fore.CYAN}Loaded configuration.")
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"{Fore.RED}Failed to load configuration: {e}")
            config = ConfigManager.DEFAULT_CONFIG

        return config

    @staticmethod
    def save_config(config):
        """Saves the given configuration to the config file."""
        with open(ConfigManager.CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file, indent=4)
            logging.info(f"{Fore.CYAN}Saved configuration to {ConfigManager.CONFIG_FILE}")

    @staticmethod
    def validate_config(config):
        """Validates and fixes invalid configuration values."""
        valid = True

        # Validate TriggerKey
        if not isinstance(config['Settings'].get('TriggerKey'), str):
            logging.error(f"{Fore.RED}Invalid TriggerKey in configuration. Resetting to default.")
            config['Settings']['TriggerKey'] = ConfigManager.DEFAULT_CONFIG['Settings']['TriggerKey']
            valid = False

        # Validate ShotDelayMin
        if not isinstance(config['Settings'].get('ShotDelayMin'), (int, float)) or config['Settings']['ShotDelayMin'] <= 0:
            logging.error(f"{Fore.RED}Invalid ShotDelayMin in configuration. Resetting to default.")
            config['Settings']['ShotDelayMin'] = ConfigManager.DEFAULT_CONFIG['Settings']['ShotDelayMin']
            valid = False

        # Validate ShotDelayMax
        if not isinstance(config['Settings'].get('ShotDelayMax'), (int, float)) or config['Settings']['ShotDelayMax'] <= 0:
            logging.error(f"{Fore.RED}Invalid ShotDelayMax in configuration. Resetting to default.")
            config['Settings']['ShotDelayMax'] = ConfigManager.DEFAULT_CONFIG['Settings']['ShotDelayMax']
            valid = False

        # Validate AttackOnTeammates
        if not isinstance(config['Settings'].get('AttackOnTeammates'), bool):
            logging.error(f"{Fore.RED}Invalid AttackOnTeammates in configuration. Resetting to default.")
            config['Settings']['AttackOnTeammates'] = ConfigManager.DEFAULT_CONFIG['Settings']['AttackOnTeammates']
            valid = False

        return valid

    @staticmethod
    def load_and_validate_config():
        """Loads and validates configuration, applying defaults where necessary."""
        config = ConfigManager.load_config()
        if not ConfigManager.validate_config(config):
            logging.info(f"{Fore.YELLOW}Configuration had invalid values. Updated with defaults.")
            ConfigManager.save_config(config)
        return config

    @staticmethod
    def reload_config():
        """Reloads configuration during runtime."""
        logging.info(f"{Fore.CYAN}Reloading configuration from file...")
        return ConfigManager.load_and_validate_config()

class Utility:
    """Contains utility functions for the application."""
    
    CACHE_DIRECTORY = ConfigManager.CONFIG_DIRECTORY
    CACHE_FILE = os.path.join(CACHE_DIRECTORY, 'offsets_cache.json')
    
    @staticmethod
    def set_console_title(title):
        ctypes.windll.kernel32.SetConsoleTitleW(title)

    @staticmethod
    def fetch_offsets():
        """Fetches offsets and client data from remote sources or local cache."""
        try:
            response_offset = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json")
            response_client = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json")
            
            if response_offset.status_code != 200 or response_client.status_code != 200:
                logging.error(f"{Fore.RED}Failed to fetch offsets from server.")
                return None, None

            offset = response_offset.json()
            client = response_client.json()

            if os.path.exists(Utility.CACHE_FILE):
                with open(Utility.CACHE_FILE, 'r') as f:
                    cached_data = json.load(f)
                
                if cached_data.get('offsets') != offset or cached_data.get('client') != client:
                    logging.info(f"{Fore.YELLOW}Offsets have changed, updating cache...")
                    with open(Utility.CACHE_FILE, 'w') as f:
                        json.dump({'offsets': offset, 'client': client}, f)
                else:
                    logging.info(f"{Fore.CYAN}Using cached offsets.")
                    return cached_data['offsets'], cached_data['client']
            else:
                os.makedirs(Utility.CACHE_DIRECTORY, exist_ok=True)
                with open(Utility.CACHE_FILE, 'w') as f:
                    json.dump({'offsets': offset, 'client': client}, f)

            return offset, client
        except Exception as e:
            logging.error(f"{Fore.RED}Failed to fetch offsets: {e}")
            return None, None

    @staticmethod
    def check_for_updates(current_version):
        """Checks for software updates on GitHub."""
        try:
            response = get("https://api.github.com/repos/Jesewe/cs2-triggerbot/tags")
            response.raise_for_status()
            latest_version = response.json()[0]["name"]
            if version.parse(latest_version) > version.parse(current_version):
                logging.warning(f"{Fore.YELLOW}New version available: {latest_version}. Please update for the latest fixes and features.")
            else:
                logging.info(f"{Fore.GREEN}You are using the latest version.")
        except Exception as e:
            logging.error(f"{Fore.RED}Error checking for updates: {e}")

class CS2TriggerBot:
    """Main class for the CS2 TriggerBot functionality."""

    VERSION = "v1.1.2"

    def __init__(self):
        """Initializes the TriggerBot with necessary attributes."""
        self.config = ConfigManager.load_and_validate_config()
        self.pm = None
        self.client_base = None
        self.dwEntityList = None
        self.dwLocalPlayerPawn = None
        self.m_iHealth = None
        self.m_iTeamNum = None
        self.m_iIDEntIndex = None
        self.is_running = False
        self.trigger_active = False  # Tracks the state of the trigger key
        self.trigger_key = self.config['Settings']['TriggerKey']  # Stores the key that activates the trigger
        self.shot_delay_min = self.config['Settings']['ShotDelayMin']  
        self.shot_delay_max = self.config['Settings']['ShotDelayMax']
        self.attack_on_teammates = self.config['Settings']['AttackOnTeammates']

    def initialize_pymem(self):
        """Initializes Pymem and attaches to the game process."""
        try:
            self.pm = pymem.Pymem("cs2.exe")
            logging.info(f"{Fore.GREEN}Successfully attached to cs2.exe process.")
        except pymem.exception.ProcessNotFound:
            logging.error(f"{Fore.RED}Could not find cs2.exe process. Please make sure the game is running.")
        except pymem.exception.PymemError as e:
            logging.error(f"{Fore.RED}Pymem encountered an error: {e}")
        except Exception as e:
            logging.error(f"{Fore.RED}Unexpected error during Pymem initialization: {e}")
        return self.pm is not None

    def get_client_module(self):
        """Retrieves the client.dll module base address."""
        try:
            if self.client_base is None:
                client_module = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
                if not client_module:
                    raise pymem.exception.ModuleNotFoundError("client.dll not found")
                self.client_base = client_module.lpBaseOfDll
                logging.info(f"{Fore.GREEN}client.dll module found at {hex(self.client_base)}.")
        except pymem.exception.ModuleNotFoundError as e:
            logging.error(f"{Fore.RED}Error: {e}. Ensure client.dll is loaded.")
        except Exception as e:
            logging.error(f"{Fore.RED}Unexpected error retrieving client module: {e}")
        return self.client_base is not None

    def get_entity(self, index):
        """Fetches an entity from the entity list."""
        try:
            ent_list = self.pm.read_longlong(self.client_base + self.dwEntityList)
            ent_entry = self.pm.read_longlong(ent_list + 0x8 * (index >> 9) + 0x10)
            return self.pm.read_longlong(ent_entry + 120 * (index & 0x1FF))
        except Exception as e:
            logging.error(f"{Fore.RED}Error reading entity: {e}")
            return None
        
    @staticmethod
    def is_game_active():
        """Checks if the game window is active."""
        return GetWindowText(GetForegroundWindow()) == "Counter-Strike 2"

    def should_trigger(self, entity_team, player_team, entity_health):
        """Determines if the trigger bot should activate based on team and health status."""
        if self.attack_on_teammates:
            return entity_health > 0  # Fire at anyone alive
        return entity_team != player_team and entity_health > 0  # Fire only at enemies

    def start(self):
        """Starts the main loop of the TriggerBot."""
        Utility.set_console_title(f"CS2 TriggerBot {self.VERSION}")

        logging.info(f"{Fore.CYAN}Checking for updates...")
        Utility.check_for_updates(self.VERSION)

        logging.info(f"{Fore.CYAN}Fetching offsets and client data...")
        offsets, client_data = Utility.fetch_offsets()
        if offsets is None or client_data is None:
            input(f"{Fore.RED}Press Enter to exit...")
            return

        # Set offsets and client data
        self.dwEntityList = offsets["client.dll"]["dwEntityList"]
        self.dwLocalPlayerPawn = offsets["client.dll"]["dwLocalPlayerPawn"]
        self.m_iHealth = client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iHealth"]
        self.m_iTeamNum = client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iTeamNum"]
        self.m_iIDEntIndex = client_data["client.dll"]["classes"]["C_CSPlayerPawnBase"]["fields"]["m_iIDEntIndex"]
        
        logging.info(f"{Fore.CYAN}Searching for cs2.exe process...")
        if not self.initialize_pymem():
            input(f"{Fore.RED}Press Enter to exit...")
            return

        if not self.get_client_module():
            input(f"{Fore.RED}Press Enter to exit...")
            return

        logging.info(f"{Fore.GREEN}TriggerBot started, trigger key: {self.trigger_key.upper()}")
        self.is_running = True

        self.run_trigger_loop()

    def run_trigger_loop(self):
        """Runs the main trigger loop."""
        while self.is_running:
            try:
                if not self.is_game_active():
                    time.sleep(0.05)
                    continue

                if keyboard.is_pressed(self.trigger_key):
                    player = self.pm.read_longlong(self.client_base + self.dwLocalPlayerPawn)
                    entity_id = self.pm.read_int(player + self.m_iIDEntIndex)
                    
                    if entity_id > 0:
                        entity = self.get_entity(entity_id)
                        if entity:
                            entity_team = self.pm.read_int(entity + self.m_iTeamNum)
                            player_team = self.pm.read_int(player + self.m_iTeamNum)
                            entity_health = self.pm.read_int(entity + self.m_iHealth)
                            
                            if self.should_trigger(entity_team, player_team, entity_health):
                                time.sleep(uniform(self.shot_delay_min, self.shot_delay_max))
                                mouse.press(Button.left)
                                time.sleep(uniform(self.shot_delay_min, self.shot_delay_max))
                                mouse.release(Button.left)

                    time.sleep(0.01)
                else:
                    time.sleep(0.05)
            except KeyboardInterrupt:
                logging.info(f"{Fore.YELLOW}TriggerBot stopped by user.")
                self.is_running = False
            except Exception as e:
                logging.error(f"{Fore.RED}Unexpected error: {e}")
                input(f"{Fore.RED}Press Enter to exit...")

if __name__ == '__main__':
    Logger.setup_logging()
    bot = CS2TriggerBot()
    bot.start()