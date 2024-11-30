import threading, pymem, pymem.process, time, psutil, random, keyboard, win32gui
from pynput.mouse import Controller, Button, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyboardListener
from classes.config_manager import ConfigManager
from classes.logger import Logger

mouse = Controller()
logger = Logger.get_logger()

class CS2TriggerBot:
    VERSION = "v1.2.0"

    def __init__(self, offsets, client_data):
        self.config = ConfigManager.load_config()
        self.offsets, self.client_data = offsets, client_data
        self.pm, self.client_base = None, None
        self.is_running, self.stop_event = False, threading.Event()
        self.trigger_active = False
        self.update_config(self.config)
        self.initialize_offsets()

        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.mouse_listener = MouseListener(on_click=self.on_mouse_click)
        
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def initialize_offsets(self):
        try:
            self.dwEntityList = self.offsets["client.dll"]["dwEntityList"]
            self.dwLocalPlayerPawn = self.offsets["client.dll"]["dwLocalPlayerPawn"]
            self.m_iHealth = self.client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iHealth"]
            self.m_iTeamNum = self.client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iTeamNum"]
            self.m_iIDEntIndex = self.client_data["client.dll"]["classes"]["C_CSPlayerPawnBase"]["fields"]["m_iIDEntIndex"]
        except KeyError as e:
            logger.error(f"Offset initialization error: {e}")
        else:
            logger.info("Offsets have been initialised.")

    def update_config(self, config):
        self.config = config
        self.trigger_key = self.config['Settings']['TriggerKey']
        self.shot_delay_min = self.config['Settings']['ShotDelayMin']
        self.shot_delay_max = self.config['Settings']['ShotDelayMax']
        self.post_shot_delay = self.config['Settings']['PostShotDelay']
        self.attack_on_teammates = self.config['Settings']['AttackOnTeammates']
        self.is_mouse_trigger = self.trigger_key in ["x1", "x2"]

    def on_key_press(self, key):
        if not self.is_mouse_trigger:
            try:
                if key.char == self.trigger_key:
                    self.trigger_active = True
            except AttributeError:
                pass

    def on_key_release(self, key):
        if not self.is_mouse_trigger:
            try:
                if key.char == self.trigger_key:
                    self.trigger_active = False
            except AttributeError:
                pass

    def on_mouse_click(self, x, y, button, pressed):
        if self.is_mouse_trigger:
            if self.trigger_key in ["x2", "x1"] and button == Button[self.trigger_key]:
                self.trigger_active = pressed

    @staticmethod
    def is_game_active():
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == "Counter-Strike 2"
    
    @staticmethod
    def is_game_running():
        return any(proc.info['name'] == 'cs2.exe' for proc in psutil.process_iter(attrs=['name']))

    def initialize_pymem(self):
        try:
            self.pm = pymem.Pymem("cs2.exe")
            logger.info(f"Successfully attached to cs2.exe process.")
        except pymem.exception.ProcessNotFound:
            logger.error("cs2.exe process not found. Ensure the game is running.")
        return self.pm is not None

    def get_client_module(self):
        if not self.client_base:
            try:
                client_module = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
                self.client_base = client_module.lpBaseOfDll
            except pymem.exception.ModuleNotFoundError:
                logger.error("client.dll not found. Ensure it is loaded.")
        return self.client_base is not None

    def get_entity(self, index):
        try:
            ent_list = self.pm.read_longlong(self.client_base + self.dwEntityList)
            ent_entry = self.pm.read_longlong(ent_list + 0x8 * (index >> 9) + 0x10)
            return self.pm.read_longlong(ent_entry + 120 * (index & 0x1FF))
        except Exception as e:
            logger.error(f"Error reading entity: {e}")
            return None

    def should_trigger(self, entity_team, player_team, entity_health):
        return (self.attack_on_teammates or entity_team != player_team) and entity_health > 0

    def perform_fire_logic(self):
        player = self.pm.read_longlong(self.client_base + self.dwLocalPlayerPawn)
        entity_id = self.pm.read_int(player + self.m_iIDEntIndex)

        if entity_id > 0:
            entity = self.get_entity(entity_id)
            if entity:
                entity_team = self.pm.read_int(entity + self.m_iTeamNum)
                player_team = self.pm.read_int(player + self.m_iTeamNum)
                entity_health = self.pm.read_int(entity + self.m_iHealth)

                if self.should_trigger(entity_team, player_team, entity_health):
                    time.sleep(random.uniform(self.shot_delay_min, self.shot_delay_max))
                    mouse.press(Button.left)
                    time.sleep(random.uniform(self.shot_delay_min, self.shot_delay_max))
                    mouse.release(Button.left)
                    time.sleep(self.post_shot_delay)

    def start(self):
        if not self.initialize_pymem() or not self.get_client_module():
            return

        self.is_running = True

        while not self.stop_event.is_set():
            try:
                if not self.is_game_active():
                    time.sleep(0.05)
                    continue

                if (self.is_mouse_trigger and self.trigger_active) or \
                    (not self.is_mouse_trigger and keyboard.is_pressed(self.trigger_key)):
                    self.perform_fire_logic()
                else:
                    time.sleep(0.05)
                    
            except KeyboardInterrupt:
                logger.info("TriggerBot stopped by user.")
                self.stop()
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

    def stop(self):
        self.is_running = False
        self.stop_event.set()
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        logger.info("TriggerBot stopped.")