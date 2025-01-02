import threading, time, random, pymem, pymem.process, keyboard

from pynput.mouse import Controller, Button, Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener

from classes.config_manager import ConfigManager
from classes.logger import Logger
from classes.utility import Utility

# Initialize mouse controller and logger
mouse = Controller()
# Initialize the logger for consistent logging
logger = Logger.get_logger()

class CS2TriggerBot:
    VERSION = "v1.2.2"

    def __init__(self, offsets: dict, client_data: dict) -> None:
        """
        Initialize the TriggerBot with offsets, configuration, and client data.
        """
        self.config = ConfigManager.load_config()
        self.offsets, self.client_data = offsets, client_data
        self.pm, self.client_base = None, None
        self.is_running, self.stop_event = False, threading.Event()
        self.trigger_active = False
        self.update_config(self.config)

        self.load_configuration()
        self.initialize_offsets()

        # Setup listeners
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.mouse_listener = MouseListener(on_click=self.on_mouse_click)
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def load_configuration(self) -> None:
        """Load and apply configuration settings."""
        settings = self.config['Settings']
        self.trigger_key = settings['TriggerKey']
        self.shot_delay_min = settings['ShotDelayMin']
        self.shot_delay_max = settings['ShotDelayMax']
        self.post_shot_delay = settings['PostShotDelay']
        self.attack_on_teammates = settings['AttackOnTeammates']
        self.is_mouse_trigger = self.trigger_key in ["x1", "x2"]

    def initialize_offsets(self) -> None:
        """Load memory offsets."""
        try:
            client = self.offsets["client.dll"]
            self.dwEntityList = client["dwEntityList"]
            self.dwLocalPlayerPawn = client["dwLocalPlayerPawn"]

            classes = self.client_data["client.dll"]["classes"]
            self.m_iHealth = classes["C_BaseEntity"]["fields"]["m_iHealth"]
            self.m_iTeamNum = classes["C_BaseEntity"]["fields"]["m_iTeamNum"]
            self.m_iIDEntIndex = classes["C_CSPlayerPawnBase"]["fields"]["m_iIDEntIndex"]
            logger.info("Offsets have been initialized.")
        except KeyError as e:
            logger.error(f"Offset initialization error: Missing key {e}")

    def update_config(self, config):
        self.config = config
        self.trigger_key = self.config['Settings']['TriggerKey']
        self.shot_delay_min = self.config['Settings']['ShotDelayMin']
        self.shot_delay_max = self.config['Settings']['ShotDelayMax']
        self.post_shot_delay = self.config['Settings']['PostShotDelay']
        self.attack_on_teammates = self.config['Settings']['AttackOnTeammates']
        self.is_mouse_trigger = self.trigger_key in ["x1", "x2"]

    def on_key_press(self, key) -> None:
        """Handle key press events."""
        if not self.is_mouse_trigger:
            try:
                if key.char == self.trigger_key:
                    self.trigger_active = True
            except AttributeError:
                pass

    def on_key_release(self, key) -> None:
        """Handle key release events."""
        if not self.is_mouse_trigger:
            try:
                if key.char == self.trigger_key:
                    self.trigger_active = False
            except AttributeError:
                pass

    def on_mouse_click(self, x, y, button, pressed) -> None:
        """Handle mouse click events."""
        if self.is_mouse_trigger and button == Button[self.trigger_key]:
            self.trigger_active = pressed

    def initialize_pymem(self) -> bool:
        """Attach pymem to the game process."""
        try:
            self.pm = pymem.Pymem("cs2.exe")
            logger.info("Successfully attached to cs2.exe process.")
            return True
        except pymem.exception.ProcessNotFound:
            logger.error("cs2.exe process not found. Ensure the game is running.")
            return False

    def get_client_module(self) -> bool:
        """Retrieve the client.dll module base address."""
        if not self.client_base:
            try:
                client_module = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
                self.client_base = client_module.lpBaseOfDll
                return True
            except pymem.exception.ModuleNotFoundError:
                logger.error("client.dll not found. Ensure it is loaded.")
        return False

    def get_entity(self, index: int):
        """Retrieve an entity from the entity list."""
        try:
            ent_list = self.pm.read_longlong(self.client_base + self.dwEntityList)
            ent_entry = self.pm.read_longlong(ent_list + 0x8 * (index >> 9) + 0x10)
            return self.pm.read_longlong(ent_entry + 120 * (index & 0x1FF))
        except Exception as e:
            logger.error(f"Error reading entity: {e}")
            return None

    def should_trigger(self, entity_team: int, player_team: int, entity_health: int) -> bool:
        """Determine if the bot should fire."""
        return (self.attack_on_teammates or entity_team != player_team) and entity_health > 0

    def perform_fire_logic(self) -> None:
        """Execute the firing logic."""
        try:
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
                        mouse.click(Button.left)
                        time.sleep(self.post_shot_delay)
        except Exception as e:
            logger.error(f"Error in fire logic: {e}")

    def start(self) -> None:
        """Start the TriggerBot."""
        if not self.initialize_pymem() or not self.get_client_module():
            return

        self.is_running = True
        logger.info("TriggerBot started.")

        while not self.stop_event.is_set():
            try:
                if not Utility.is_game_active():
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
                logger.error(f"Unexpected error in start loop: {e}", exc_info=True)

    def stop(self) -> None:
        """
        Stops the TriggerBot and cleans up resources.
        Also stops the keyboard and mouse listeners.
        """
        self.is_running = False
        self.stop_event.set()
        if self.keyboard_listener.running:
            self.keyboard_listener.stop()
        if self.mouse_listener.running:
            self.mouse_listener.stop()
        logger.info(f"TriggerBot stopped.")