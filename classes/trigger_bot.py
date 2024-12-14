import threading, pymem, pymem.process, time, psutil, random, keyboard, win32gui
from pynput.mouse import Controller, Button, Listener as MouseListener
from pynput.keyboard import Key, Listener as KeyboardListener
from classes.config_manager import ConfigManager
from classes.logger import Logger

# Initialize mouse controller for emulating mouse clicks.
mouse = Controller()
# Get a logger instance for consistent logging.
logger = Logger.get_logger()

class CS2TriggerBot:
    # Define the current version of the TriggerBot for reference.
    VERSION = "v1.2.0"

    def __init__(self, offsets, client_data):
        """
        Initialize the TriggerBot with offsets, configuration, and client data.
        Sets up listeners for keyboard and mouse events.
        """
        # Load initial configuration and data
        self.config = ConfigManager.load_config()
        self.offsets = offsets
        self.client_data = client_data
        
        # Memory-related attributes
        self.pm = None
        self.client_base = None
        
        # Thread control and state flags
        self.is_running = False
        self.stop_event = threading.Event()
        self.trigger_active = False
        
        # Initialize bot settings
        self.update_config(self.config)
        self.initialize_offsets()

        # Setup input listeners
        self._setup_input_listeners()

    def _setup_input_listeners(self):
        """
        Helper method to setup and start keyboard/mouse listeners
        """
        self.keyboard_listener = KeyboardListener(
            on_press=self.on_key_press, 
            on_release=self.on_key_release
        )
        self.mouse_listener = MouseListener(on_click=self.on_mouse_click)
        
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def initialize_offsets(self):
        """
        Initialize required offsets from the given client data.
        Ensures memory addresses for critical game data are ready.
        """
        try:
            # Extract offsets from client data
            self.dwEntityList = self.offsets["client.dll"]["dwEntityList"]
            self.dwLocalPlayerPawn = self.offsets["client.dll"]["dwLocalPlayerPawn"]
            
            # Get entity class fields
            base_entity = self.client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]
            self.m_iHealth = base_entity["m_iHealth"]
            self.m_iTeamNum = base_entity["m_iTeamNum"]
            
            # Get player pawn fields
            self.m_iIDEntIndex = self.client_data["client.dll"]["classes"]["C_CSPlayerPawnBase"]["fields"]["m_iIDEntIndex"]
            
            logger.info("Offsets have been initialized.")
            
        except KeyError as e:
            logger.error(f"Offset initialization error: {e}")

    def update_config(self, config):
        """
        Update the configuration settings for the TriggerBot.
        Retrieves relevant settings such as keys, delays, and team attack preference.
        """
        self.config = config
        settings = config['Settings']
        
        # Extract settings
        self.trigger_key = settings['TriggerKey']
        self.shot_delay_min = settings['ShotDelayMin']
        self.shot_delay_max = settings['ShotDelayMax']
        self.post_shot_delay = settings['PostShotDelay']
        self.attack_on_teammates = settings['AttackOnTeammates']
        
        # Determine if using mouse trigger
        self.is_mouse_trigger = self.trigger_key in ["x1", "x2"]

    def on_key_press(self, key):
        """
        Handles key press events for activating the trigger.
        Activates when the trigger key is pressed (non-mouse triggers).
        """
        if not self.is_mouse_trigger:
            try:
                if key.char == self.trigger_key:
                    self.trigger_active = True
            except AttributeError:
                pass

    def on_key_release(self, key):
        """
        Handles key release events for deactivating the trigger.
        Deactivates when the trigger key is released (non-mouse triggers).
        """
        if not self.is_mouse_trigger:
            try:
                if key.char == self.trigger_key:
                    self.trigger_active = False
            except AttributeError:
                pass

    def on_mouse_click(self, x, y, button, pressed):
        """
        Handles mouse click events for activating/deactivating the trigger.
        Activates when the specified mouse button is pressed.
        """
        if self.is_mouse_trigger:
            if self.trigger_key in ["x2", "x1"] and button == Button[self.trigger_key]:
                self.trigger_active = pressed

    @staticmethod
    def is_game_active():
        """
        Checks if the game window (Counter-Strike 2) is currently active.
        """
        return win32gui.GetWindowText(win32gui.GetForegroundWindow()) == "Counter-Strike 2"

    @staticmethod
    def is_game_running():
        """
        Checks if the game process (cs2.exe) is currently running.
        """
        return any(proc.info['name'] == 'cs2.exe' for proc in psutil.process_iter(attrs=['name']))

    def initialize_pymem(self):
        """
        Attaches pymem to the game process (cs2.exe) for memory reading.
        """
        try:
            self.pm = pymem.Pymem("cs2.exe")
            logger.info(f"Successfully attached to cs2.exe process.")
            return True
        except pymem.exception.ProcessNotFound:
            logger.error("cs2.exe process not found. Ensure the game is running.")
            return False

    def get_client_module(self):
        """
        Retrieves the client.dll module base address for memory operations.
        """
        if not self.client_base:
            try:
                client_module = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
                self.client_base = client_module.lpBaseOfDll
                return True
            except pymem.exception.ModuleNotFoundError:
                logger.error("client.dll not found. Ensure it is loaded.")
                return False
        return True

    def get_entity(self, index):
        """
        Retrieves an entity from the entity list by its index.
        """
        try:
            ent_list = self.pm.read_longlong(self.client_base + self.dwEntityList)
            ent_entry = self.pm.read_longlong(ent_list + 0x8 * (index >> 9) + 0x10)
            return self.pm.read_longlong(ent_entry + 120 * (index & 0x1FF))
        except Exception as e:
            logger.error(f"Error reading entity: {e}")
            return None

    def should_trigger(self, entity_team, player_team, entity_health):
        """
        Determines if the bot should fire based on team and health conditions.
        """
        return (self.attack_on_teammates or entity_team != player_team) and entity_health > 0

    def perform_fire_logic(self):
        """
        Performs the firing logic for the bot:
        - Reads player and entity data.
        - Simulates a mouse click if conditions are met.
        """
        # Get local player and target entity
        player = self.pm.read_longlong(self.client_base + self.dwLocalPlayerPawn)
        entity_id = self.pm.read_int(player + self.m_iIDEntIndex)

        if entity_id > 0:
            entity = self.get_entity(entity_id)
            if entity:
                # Read entity data
                entity_team = self.pm.read_int(entity + self.m_iTeamNum)
                player_team = self.pm.read_int(player + self.m_iTeamNum)
                entity_health = self.pm.read_int(entity + self.m_iHealth)

                # Check if should trigger and perform click
                if self.should_trigger(entity_team, player_team, entity_health):
                    self._simulate_mouse_click()

    def _simulate_mouse_click(self):
        """
        Helper method to simulate mouse click with configured delays
        """
        time.sleep(random.uniform(self.shot_delay_min, self.shot_delay_max))
        mouse.press(Button.left)
        time.sleep(random.uniform(self.shot_delay_min, self.shot_delay_max))
        mouse.release(Button.left)
        time.sleep(self.post_shot_delay)

    def start(self):
        """
        Starts the TriggerBot functionality:
        - Initializes pymem and client module.
        - Runs the bot in a loop, monitoring trigger activation.
        """
        # Initialize memory access
        if not self.initialize_pymem() or not self.get_client_module():
            return

        self.is_running = True

        while not self.stop_event.is_set():
            try:
                # Check game window focus
                if not self.is_game_active():
                    time.sleep(0.05)
                    continue

                # Check trigger activation
                is_trigger_active = (self.is_mouse_trigger and self.trigger_active) or \
                                  (not self.is_mouse_trigger and keyboard.is_pressed(self.trigger_key))
                
                if is_trigger_active:
                    self.perform_fire_logic()
                else:
                    time.sleep(0.05)

            except KeyboardInterrupt:
                logger.info("TriggerBot stopped by user.")
                self.stop()
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

    def stop(self):
        """
        Stops the TriggerBot and cleans up resources.
        """
        self.is_running = False
        self.stop_event.set()
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        logger.info("TriggerBot stopped.")
