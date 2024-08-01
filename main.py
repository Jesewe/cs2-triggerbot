import pymem, pymem.process, keyboard, time
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
from random import uniform
import logging
from requests import get

mouse = Controller()

def fetch_offsets():
    try:
        offset = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json").json()
        client = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json").json()
        return offset, client
    except Exception as e:
        logging.error(f"Failed to fetch offsets: {e}")
        return None, None

def initialize_pymem():
    try:
        pm = pymem.Pymem("cs2.exe")
        return pm
    except pymem.exception.PymemError as e:
        logging.error(f"Could not open cs2.exe: {e}")
        return None

def get_client_module(pm):
    client_module = pymem.process.module_from_name(pm.process_handle, "client.dll")
    if not client_module:
        logging.error("Could not find client.dll module.")
        return None
    return client_module.lpBaseOfDll

def get_entity(pm, base_address, index):
    try:
        ent_list = pm.read_longlong(base_address + dwEntityList)
        ent_entry = pm.read_longlong(ent_list + 0x8 * (index >> 9) + 0x10)
        return pm.read_longlong(ent_entry + 120 * (index & 0x1FF))
    except Exception as e:
        logging.error(f"Error reading entity: {e}")
        return None

def is_game_active():
    return GetWindowText(GetForegroundWindow()) == application_name

def should_trigger(entity_team, player_team, entity_health):
    return entity_team != player_team and entity_health > 0

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f"TriggerBot started. Trigger key: {triggerKey.upper()}")

    offsets, client_data = fetch_offsets()
    if offsets is None or client_data is None:
        return

    global dwEntityList, dwLocalPlayerPawn, m_iHealth, m_iTeamNum, m_iIDEntIndex
    dwEntityList = offsets["client.dll"]["dwEntityList"]
    dwLocalPlayerPawn = offsets["client.dll"]["dwLocalPlayerPawn"]
    m_iHealth = client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iHealth"]
    m_iTeamNum = client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iTeamNum"]
    m_iIDEntIndex = client_data["client.dll"]["classes"]["C_CSPlayerPawnBase"]["fields"]["m_iIDEntIndex"]

    pm = initialize_pymem()
    if pm is None:
        return

    client_base = get_client_module(pm)
    if client_base is None:
        return

    while True:
        try:
            if not is_game_active():
                time.sleep(0.1)
                continue

            if keyboard.is_pressed(triggerKey):
                player = pm.read_longlong(client_base + dwLocalPlayerPawn)
                entity_id = pm.read_int(player + m_iIDEntIndex)
                
                if entity_id > 0:
                    entity = get_entity(pm, client_base, entity_id)
                    if entity:
                        entity_team = pm.read_int(entity + m_iTeamNum)
                        player_team = pm.read_int(player + m_iTeamNum)
                        entity_health = pm.read_int(entity + m_iHealth)
                        
                        if should_trigger(entity_team, player_team, entity_health):
                            time.sleep(uniform(0.01, 0.03))
                            mouse.press(Button.left)
                            time.sleep(uniform(0.01, 0.05))
                            mouse.release(Button.left)

                time.sleep(0.03)
            else:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logging.info("TriggerBot stopped by user.")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    application_name = "Counter-Strike 2"
    triggerKey = "X"
    main()