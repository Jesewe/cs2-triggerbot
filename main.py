import pymem
import pymem.process
import time
import os
import ctypes
from pynput.mouse import Controller, Button
from pynput.mouse import Listener as MouseListener
from pynput import keyboard
from win32gui import GetWindowText, GetForegroundWindow
from random import uniform
import logging
from requests import get
from packaging import version
from colorama import init, Fore
import json
import configparser

# Initialize colorama for colored console output
init(autoreset=True)

# Initialize mouse controller for trigger actions
mouse = Controller()

class Logger:
    """Handles logging setup for the application."""
    
    LOG_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe\crashes')
    LOG_FILE = os.path.join(LOG_DIRECTORY, 'tb_logs.log')

    @staticmethod
    def setup_logging(log_level):
        """Set up the logging configuration with the specified log level."""
        os.makedirs(Logger.LOG_DIRECTORY, exist_ok=True)
        with open(Logger.LOG_FILE, 'w') as f:
            pass
        
        # Convert log level string to logging module constant
        log_levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        level = log_levels.get(log_level.upper(), logging.INFO)  # Default to INFO if invalid
        
        logging.basicConfig(
            level=level,
            format='%(levelname)s: %(message)s',
            handlers=[logging.FileHandler(Logger.LOG_FILE), logging.StreamHandler()]
        )

class Utility:
    """Contains utility functions for the application."""

    CACHE_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe')
    CACHE_FILE = os.path.join(CACHE_DIRECTORY, 'offsets_cache.json')
    
    @staticmethod
    def set_console_title(title):
        """Sets the console window title."""
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
            logging.error(f"{Fore.RED}Please report this issue on the GitHub repository: https://github.com/Jesewe/cs2-triggerbot/issues")
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
    
    VERSION = "v1.1.1"

    def __init__(self):
        """Initializes the TriggerBot with necessary attributes."""
        self.pm = None
        self.client_base = None
        self.dwEntityList = None
        self.dwLocalPlayerPawn = None
        self.m_iHealth = None
        self.m_iTeamNum = None
        self.m_iIDEntIndex = None
        self.is_running = False
        self.trigger_active = False  # Tracks the state of the trigger key
        self.trigger_key = None  # Stores the key that activates the trigger
        self.attack_on_teammates = False  # New setting for attacking teammates
        self.load_config()  # Load trigger key and other settings from config.ini

    def load_config(self):
        """Loads the configuration from config.ini, adding missing settings if necessary."""
        config = configparser.ConfigParser()
        config_file = os.path.join(Utility.CACHE_DIRECTORY, 'config.ini')

        if not os.path.exists(config_file):
            logging.info(f"{Fore.YELLOW}config.ini not found. Creating a default config.ini...")
            config['Settings'] = {
                'TriggerKey': 'x2',  # Default to MOUSE 5
                'ShotDelayMin': '0.01',  # Default minimum delay
                'ShotDelayMax': '0.03',  # Default maximum delay
                'AttackOnTeammates': 'False'  # Default to not attacking teammates
            }
            config['Logger'] = {
                'LogLevel': 'INFO'  # Default logging level
            }
            os.makedirs(Utility.CACHE_DIRECTORY, exist_ok=True)
            with open(config_file, 'w') as f:
                config.write(f)
        else:
            # Load the existing config file
            config.read(config_file)
            
            # Check if the new settings are missing, and add them with default values if needed
            if 'ShotDelayMin' not in config['Settings']:
                config['Settings']['ShotDelayMin'] = '0.01'
            if 'ShotDelayMax' not in config['Settings']:
                config['Settings']['ShotDelayMax'] = '0.03'
            if 'AttackOnTeammates' not in config['Settings']:
                config['Settings']['AttackOnTeammates'] = 'False'
            
            if 'Logger' not in config:
                config['Logger'] = {'LogLevel': 'INFO'}  # Add Logger section if missing
            elif 'LogLevel' not in config['Logger']:
                config['Logger']['LogLevel'] = 'INFO'

            # Save updated config file with new settings if necessary
            with open(config_file, 'w') as configfile:
                config.write(configfile)

        # Load settings
        self.trigger_key = config['Settings']['TriggerKey']
        self.shot_delay_min = float(config['Settings'].get('ShotDelayMin', 0.01))
        self.shot_delay_max = float(config['Settings'].get('ShotDelayMax', 0.03))
        self.log_level = config['Logger']['LogLevel']
        self.attack_on_teammates = config['Settings'].getboolean('AttackOnTeammates', False)

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
            self.handle_retry_or_exit("client.dll module not found")
        except Exception as e:
            logging.error(f"{Fore.RED}Unexpected error retrieving client module: {e}")
            self.handle_retry_or_exit("Unexpected client module error")
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
        # If AttackOnTeammates is True, ignore team checks and only fire based on health
        if self.attack_on_teammates:
            return entity_health > 0  # Fire at anyone alive
        # If AttackOnTeammates is False, only fire at enemies
        return entity_team != player_team and entity_health > 0  # Fire only at enemies

    def on_mouse_press(self, x, y, button, pressed):
        """Mouse press event handler."""
        if self.trigger_key in ["x2", "x1"] and button == Button[self.trigger_key]:
            self.trigger_active = pressed

    def on_key_press(self, key):
        """Keyboard press event handler."""
        if hasattr(key, 'char') and key.char == self.trigger_key:
            self.trigger_active = True

    def on_key_release(self, key):
        """Keyboard release event handler."""
        if hasattr(key, 'char') and key.char == self.trigger_key:
            self.trigger_active = False

    def start(self):
        """Starts the main loop of the TriggerBot."""
        Utility.set_console_title(f"CS2 TriggerBot {self.VERSION}")
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

        # Initialize listeners
        self.mouse_listener = MouseListener(on_click=self.on_mouse_press)
        self.key_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.mouse_listener.start()
        self.key_listener.start()

        self.run_trigger_loop()

        # Stop listeners on exit
        self.mouse_listener.stop()
        self.key_listener.stop()

    def run_trigger_loop(self):
        """Runs the main trigger loop."""
        while self.is_running:
            try:
                if not self.is_game_active():
                    time.sleep(0.05)
                    continue

                if self.trigger_active:
                    player = self.pm.read_longlong(self.client_base + self.dwLocalPlayerPawn)
                    entity_id = self.pm.read_int(player + self.m_iIDEntIndex)
                    
                    if entity_id > 0:
                        entity = self.get_entity(entity_id)
                        if entity:
                            entity_team = self.pm.read_int(entity + self.m_iTeamNum)
                            player_team = self.pm.read_int(player + self.m_iTeamNum)
                            entity_health = self.pm.read_int(entity + self.m_iHealth)
                            
                            if self.should_trigger(entity_team, player_team, entity_health):
                                # Use random delays from the configuration
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
                logging.error(f"{Fore.RED}Please report this issue on the GitHub repository: https://github.com/Jesewe/cs2-triggerbot/issues")
                input(f"{Fore.RED}Press Enter to exit...")

if __name__ == '__main__':
    bot = CS2TriggerBot()
    Logger.setup_logging(bot.log_level)
    bot.start()