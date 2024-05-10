import pymem, pymem.process, keyboard, time
from pynput.mouse import Controller, Button
from win32gui import GetWindowText, GetForegroundWindow
from random import uniform
import logging
from requests import get

mouse = Controller()

offset = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json").json()
client = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client.dll.json").json()

dwEntityList = offset["client.dll"]["dwEntityList"]
dwLocalPlayerPawn = offset["client.dll"]["dwLocalPlayerPawn"]
m_iHealth = client["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iHealth"]
m_iTeamNum = client["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iTeamNum"]
m_iIDEntIndex = client["client.dll"]["classes"]["C_CSPlayerPawnBase"]["fields"]["m_iIDEntIndex"]
    
application_name = "Counter-Strike 2"
triggerKey = "X"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def triggerbot():
    logging.info(f"TriggerBot started. Trigger key: {triggerKey.upper()}")
    try:
        pm = pymem.Pymem("cs2.exe")
    except pymem.exception.PymemError as e:
        logging.error(f"Could not open cs2.exe: {e}")
        return

    client_module = pymem.process.module_from_name(pm.process_handle, "client.dll")
    if not client_module:
        logging.error("Could not find client.dll module.")
        return

    client = client_module.lpBaseOfDll

    while True:
        try:
            if GetWindowText(GetForegroundWindow()) != application_name:
                time.sleep(0.1)
                continue

            if keyboard.is_pressed(triggerKey):
                player = pm.read_longlong(client + dwLocalPlayerPawn)
                entityId = pm.read_int(player + m_iIDEntIndex)

                if entityId > 0:
                    entList = pm.read_longlong(client + dwEntityList)
                    entEntry = pm.read_longlong(entList + 0x8 * (entityId >> 9) + 0x10)
                    entity = pm.read_longlong(entEntry + 120 * (entityId & 0x1FF))

                    entityTeam = pm.read_int(entity + m_iTeamNum)
                    playerTeam = pm.read_int(player + m_iTeamNum)

                    if entityTeam != playerTeam:
                        entityHp = pm.read_int(entity + m_iHealth)
                        if entityHp > 0:
                            time.sleep(uniform(0.01, 0.03))
                            mouse.press(Button.left)
                            time.sleep(uniform(0.01, 0.05))
                            mouse.release(Button.left)

                time.sleep(0.03)
            else:
                time.sleep(0.1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            pass

if __name__ == '__main__':
    triggerbot()