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
from colorama import init, Fore, Style

# Initialize colorama for colored console output
init(autoreset=True)

# Initialize mouse controller for trigger actions
mouse = Controller()

# Define version and constants
VERSION = "v1.0.7"
TRIGGER_KEY = 'X'  # Key to activate the trigger bot
LOG_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe\crashes')
LOG_FILE = os.path.join(LOG_DIRECTORY, 'logs.log')

# Ensure log directory exists
os.makedirs(LOG_DIRECTORY, exist_ok=True)

# Set up logging
with open(LOG_FILE, 'w') as f:
    pass

logging.basicConfig(
    level=logging.INFO,
    format=f'%(levelname)s: %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

# Function to set the console window title
def set_console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

# Function to fetch offsets and client data from remote sources
def fetch_offsets():
    try:
        offset = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json").json()
        client = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json").json()
        return offset, client
    except Exception as e:
        logging.error(f"{Fore.RED}Failed to fetch offsets: {e}")
        logging.error(f"{Fore.RED}Please report this issue on the GitHub repository: https://github.com/Jesewe/cs2-triggerbot/issues")
        return None, None

# Function to check for software updates
def check_for_updates():
    try:
        response = get("https://api.github.com/repos/Jesewe/cs2-triggerbot/tags")
        response.raise_for_status()
        latest_version = response.json()[0]["name"]
        if version.parse(latest_version) > version.parse(VERSION):
            logging.info(f"{Fore.YELLOW}New version available: {latest_version}. Please update for the latest fixes and features.")
        else:
            logging.info(f"{Fore.GREEN}You are using the latest version.")
    except Exception as e:
        logging.error(f"{Fore.RED}Error checking for updates: {e}")

# Function to initialize Pymem and attach to the game process
def initialize_pymem():
    try:
        return pymem.Pymem("cs2.exe")
    except pymem.exception.PymemError as e:
        logging.error(f"{Fore.RED}Could not open cs2.exe: {e}")
        return None

# Function to retrieve the client.dll module base address
def get_client_module(pm):
    client_module = pymem.process.module_from_name(pm.process_handle, "client.dll")
    if not client_module:
        logging.error(f"{Fore.RED}Could not find client.dll module.")
        return None
    return client_module.lpBaseOfDll

# Function to get an entity from the entity list
def get_entity(pm, base_address, index):
    try:
        ent_list = pm.read_longlong(base_address + dwEntityList)
        ent_entry = pm.read_longlong(ent_list + 0x8 * (index >> 9) + 0x10)
        return pm.read_longlong(ent_entry + 120 * (index & 0x1FF))
    except Exception as e:
        logging.error(f"{Fore.RED}Error reading entity: {e}")
        return None

# Function to check if the game window is active
def is_game_active():
    return GetWindowText(GetForegroundWindow()) == "Counter-Strike 2"

# Function to determine if the trigger bot should activate
def should_trigger(entity_team, player_team, entity_health):
    return entity_team != player_team and entity_health > 0

# Main function
def main():
    set_console_title(f"CS2 TriggerBot {VERSION}")
    check_for_updates()
    logging.info(f"{Fore.CYAN}Fetching offsets and client data...")

    # Fetch offsets and client data
    offsets, client_data = fetch_offsets()
    if offsets is None or client_data is None:
        input(f"{Fore.RED}Press Enter to exit...")
        return

    # Global variables for offsets
    global dwEntityList, dwLocalPlayerPawn, m_iHealth, m_iTeamNum, m_iIDEntIndex
    dwEntityList = offsets["client.dll"]["dwEntityList"]
    dwLocalPlayerPawn = offsets["client.dll"]["dwLocalPlayerPawn"]
    m_iHealth = client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iHealth"]
    m_iTeamNum = client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iTeamNum"]
    m_iIDEntIndex = client_data["client.dll"]["classes"]["C_CSPlayerPawnBase"]["fields"]["m_iIDEntIndex"]

    # Attempt to attach to the game process
    logging.info(f"{Fore.CYAN}Searching for cs2.exe process...")
    pm = initialize_pymem()
    if pm is None:
        input(f"{Fore.RED}Press Enter to exit...")
        return

    # Get client.dll base address
    client_base = get_client_module(pm)
    if client_base is None:
        input(f"{Fore.RED}Press Enter to exit...")
        return

    logging.info(f"{Fore.GREEN}TriggerBot started, trigger key: {TRIGGER_KEY}")

    # Main loop
    while True:
        try:
            if not is_game_active():
                time.sleep(0.05)
                continue

            if keyboard.is_pressed(TRIGGER_KEY):
                # Read player and entity data
                player = pm.read_longlong(client_base + dwLocalPlayerPawn)
                entity_id = pm.read_int(player + m_iIDEntIndex)
                
                if entity_id > 0:
                    entity = get_entity(pm, client_base, entity_id)
                    if entity:
                        entity_team = pm.read_int(entity + m_iTeamNum)
                        player_team = pm.read_int(player + m_iTeamNum)
                        entity_health = pm.read_int(entity + m_iHealth)
                        
                        if should_trigger(entity_team, player_team, entity_health):
                            # Simulate a mouse click
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
    main()