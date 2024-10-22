import dearpygui.dearpygui as dpg
import logging
import pymem
import pymem.process
import time
import os
import ctypes
import threading
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
from random import uniform
import json
import keyboard
from requests import get
from packaging import version
from colorama import init, Fore

init(autoreset=True)
mouse = Controller()

class Logger:
    LOG_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe\crashes')
    LOG_FILE = os.path.join(LOG_DIRECTORY, 'tb_logs.log')

    @staticmethod
    def setup_logging():
        os.makedirs(Logger.LOG_DIRECTORY, exist_ok=True)
        with open(Logger.LOG_FILE, 'w') as f:
            pass
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s',
            handlers=[logging.FileHandler(Logger.LOG_FILE), logging.StreamHandler()]
        )

class Utility:
    """Contains utility functions for the application."""
    
    CACHE_DIRECTORY = r'C:\Users\w\AppData\Local\Temp\cs2_triggerbot'
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

class ConfigManager:
    CONFIG_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe')
    CONFIG_FILE = os.path.join(CONFIG_DIRECTORY, 'config.json')
    
    DEFAULT_CONFIG = {
        "Settings": {
            "TriggerKey": "x",
            "ShotDelayMin": 0.01,
            "ShotDelayMax": 0.03,
            "AttackOnTeammates": False
        }
    }

    @staticmethod
    def load_config():
        if not os.path.exists(ConfigManager.CONFIG_DIRECTORY):
            os.makedirs(ConfigManager.CONFIG_DIRECTORY)
        if not os.path.exists(ConfigManager.CONFIG_FILE):
            ConfigManager.save_config(ConfigManager.DEFAULT_CONFIG)
        try:
            with open(ConfigManager.CONFIG_FILE, 'r') as config_file:
                return json.load(config_file)
        except (json.JSONDecodeError, IOError):
            return ConfigManager.DEFAULT_CONFIG

    @staticmethod
    def save_config(config):
        with open(ConfigManager.CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file, indent=4)

    @staticmethod
    def validate_config(config):
        valid = True
        if not isinstance(config['Settings'].get('TriggerKey'), str):
            config['Settings']['TriggerKey'] = ConfigManager.DEFAULT_CONFIG['Settings']['TriggerKey']
            valid = False
        if not isinstance(config['Settings'].get('ShotDelayMin'), (int, float)) or config['Settings']['ShotDelayMin'] <= 0:
            config['Settings']['ShotDelayMin'] = ConfigManager.DEFAULT_CONFIG['Settings']['ShotDelayMin']
            valid = False
        if not isinstance(config['Settings'].get('ShotDelayMax'), (int, float)) or config['Settings']['ShotDelayMax'] <= 0:
            config['Settings']['ShotDelayMax'] = ConfigManager.DEFAULT_CONFIG['Settings']['ShotDelayMax']
            valid = False
        if not isinstance(config['Settings'].get('AttackOnTeammates'), bool):
            config['Settings']['AttackOnTeammates'] = ConfigManager.DEFAULT_CONFIG['Settings']['AttackOnTeammates']
            valid = False
        return valid

    @staticmethod
    def load_and_validate_config():
        config = ConfigManager.load_config()
        if not ConfigManager.validate_config(config):
            ConfigManager.save_config(config)
        return config

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
        self.trigger_active = False
        self.trigger_key = self.config['Settings']['TriggerKey']
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
            return entity_health > 0
        return entity_team != player_team and entity_health > 0

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

    def update_config(self):
        """Update the trigger bot configuration from the loaded config."""
        self.trigger_key = self.config['Settings']['TriggerKey']
        self.shot_delay_min = self.config['Settings']['ShotDelayMin']
        self.shot_delay_max = self.config['Settings']['ShotDelayMax']
        self.attack_on_teammates = self.config['Settings']['AttackOnTeammates']

class TriggerBotGUI:
    def __init__(self):
        self.bot = CS2TriggerBot()
        self.config = self.bot.config

        dpg.create_context()
        self.build_gui()
        dpg.create_viewport(title="github.com/Jesewe/cs2-triggerbot", width=400, height=400)
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def on_press_trigger_key(self):
        print("Press a key to assign...")
        key = keyboard.read_key()
        print(f"Assigned: {key}")
        self.config['Settings']['TriggerKey'] = key
        dpg.set_value("trigger_key", key)
        self.bot.update_config()

    def build_gui(self):
        with dpg.window(tag="primary_window"):
            dpg.set_primary_window("primary_window", True)
            dpg.add_input_text(label="Trigger Key", default_value=self.config['Settings']['TriggerKey'], callback=self.update_trigger_key, tag="trigger_key")
            dpg.add_button(label="Assign Trigger Key", callback=lambda: threading.Thread(target=self.on_press_trigger_key).start())
            dpg.add_input_float(label="Shot Delay Min", default_value=self.config['Settings']['ShotDelayMin'], callback=self.update_shot_delay_min, tag="shot_delay_min")
            dpg.add_input_float(label="Shot Delay Max", default_value=self.config['Settings']['ShotDelayMax'], callback=self.update_shot_delay_max, tag="shot_delay_max")
            dpg.add_checkbox(label="Attack on Teammates", default_value=self.config['Settings']['AttackOnTeammates'], callback=self.update_attack_on_teammates, tag="attack_on_teammates")
            dpg.add_button(label="Save Config", callback=self.save_config)
            dpg.add_text("CS2 TriggerBot v1.1.3", pos=(110, 170))

    def save_config(self):
        """Saves the current configuration to the config file."""
        ConfigManager.save_config(self.config)
        logging.info("Configuration saved.")

    def update_trigger_key(self, sender, app_data, user_data):
        self.config['Settings']['TriggerKey'] = app_data
        self.bot.update_config()

    def update_shot_delay_min(self, sender, app_data, user_data):
        self.config['Settings']['ShotDelayMin'] = app_data
        self.bot.update_config()

    def update_shot_delay_max(self, sender, app_data, user_data):
        self.config['Settings']['ShotDelayMax'] = app_data
        self.bot.update_config()

    def update_attack_on_teammates(self, sender, app_data, user_data):
        self.config['Settings']['AttackOnTeammates'] = app_data
        self.bot.update_config()

    def load_config(self):
        self.config = ConfigManager.load_and_validate_config()
        logging.info("Configuration loaded.")
        dpg.set_value("trigger_key", self.config['Settings']['TriggerKey'])
        dpg.set_value("shot_delay_min", self.config['Settings']['ShotDelayMin'])
        dpg.set_value("shot_delay_max", self.config['Settings']['ShotDelayMax'])
        dpg.set_value("attack_on_teammates", self.config['Settings']['AttackOnTeammates'])
        self.bot.update_config()
        
    def run(self):
        trigger_thread = threading.Thread(target=self.bot.start)
        trigger_thread.daemon = True
        trigger_thread.start()
        dpg.start_dearpygui()

if __name__ == '__main__':
    Logger.setup_logging()
    gui = TriggerBotGUI()
    gui.run()
