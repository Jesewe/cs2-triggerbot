import pymem
import pymem.process
import time
import keyboard
import os
import ctypes
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
from random import uniform
import logging
from requests import get
from packaging import version
from colorama import init, Fore

# Initialize colorama for colored console output
init(autoreset=True)

# Initialize mouse controller for trigger actions
mouse = Controller()

class Logger:
    """Handles logging setup for the application."""
    
    LOG_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe\crashes')
    LOG_FILE = os.path.join(LOG_DIRECTORY, 'logs.log')

    @staticmethod
    def setup_logging():
        """Set up the logging configuration."""
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

    @staticmethod
    def set_console_title(title):
        """Sets the console window title."""
        ctypes.windll.kernel32.SetConsoleTitleW(title)

    @staticmethod
    def fetch_offsets():
        """Fetches offsets and client data from remote sources."""
        try:
            offset = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json").json()
            client = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json").json()
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
                logging.info(f"{Fore.YELLOW}New version available: {latest_version}. Please update for the latest fixes and features.")
            else:
                logging.info(f"{Fore.GREEN}You are using the latest version.")
        except Exception as e:
            logging.error(f"{Fore.RED}Error checking for updates: {e}")

class CS2TriggerBot:
    """Main class for the CS2 TriggerBot functionality."""
    
    VERSION = "v1.0.8"
    TRIGGER_KEY = 'X'

    def __init__(self):
        """Initializes the TriggerBot with necessary attributes."""
        self.pm = None
        self.client_base = None
        self.dwEntityList = None
        self.dwLocalPlayerPawn = None
        self.m_iHealth = None
        self.m_iTeamNum = None
        self.m_iIDEntIndex = None

    def initialize_pymem(self):
        """Initializes Pymem and attaches to the game process."""
        try:
            self.pm = pymem.Pymem("cs2.exe")
        except pymem.exception.PymemError as e:
            logging.error(f"{Fore.RED}Could not open cs2.exe: {e}")
            return False
        return True

    def get_client_module(self):
        """Retrieves the client.dll module base address."""
        client_module = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
        if not client_module:
            logging.error(f"{Fore.RED}Could not find client.dll module.")
            return False
        self.client_base = client_module.lpBaseOfDll
        return True

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
        return entity_team != player_team and entity_health > 0

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

        logging.info(f"{Fore.GREEN}TriggerBot started, trigger key: {self.TRIGGER_KEY}")

        # Main loop
        while True:
            try:
                if not self.is_game_active():
                    time.sleep(0.05)
                    continue

                if keyboard.is_pressed(self.TRIGGER_KEY):
                    player = self.pm.read_longlong(self.client_base + self.dwLocalPlayerPawn)
                    entity_id = self.pm.read_int(player + self.m_iIDEntIndex)
                    
                    if entity_id > 0:
                        entity = self.get_entity(entity_id)
                        if entity:
                            entity_team = self.pm.read_int(entity + self.m_iTeamNum)
                            player_team = self.pm.read_int(player + self.m_iTeamNum)
                            entity_health = self.pm.read_int(entity + self.m_iHealth)
                            
                            if self.should_trigger(entity_team, player_team, entity_health):
                                time.sleep(uniform(0.01, 0.02))
                                mouse.press(Button.left)
                                time.sleep(uniform(0.01, 0.03))
                                mouse.release(Button.left)

                    time.sleep(0.01)
                else:
                    time.sleep(0.05)
            except KeyboardInterrupt:
                logging.info(f"{Fore.YELLOW}TriggerBot stopped by user.")
                break
            except Exception as e:
                logging.error(f"{Fore.RED}Unexpected error: {e}")
                logging.error(f"{Fore.RED}Please report this issue on the GitHub repository: https://github.com/Jesewe/cs2-triggerbot/issues")
                input(f"{Fore.RED}Press Enter to exit...")

if __name__ == '__main__':
    Logger.setup_logging()
    bot = CS2TriggerBot()
    bot.start()