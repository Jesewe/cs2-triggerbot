import threading, time, random, keyboard, winsound

from pynput.mouse import Controller, Button, Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener

from classes.config_manager import ConfigManager
from classes.memory_manager import MemoryManager
from classes.logger import Logger
from classes.utility import Utility

# Initialize mouse controller and logger
mouse = Controller()
# Initialize the logger for consistent logging
logger = Logger.get_logger()
# Define the main loop sleep time for reduced CPU usage
MAIN_LOOP_SLEEP = 0.05

class CS2TriggerBot:
    def __init__(self, offsets: dict, client_data: dict, buttons_data: dict) -> None:
        """
        Initialize the TriggerBot with offsets, configuration, and client data.
        """
        # Load the configuration settings
        self.config = ConfigManager.load_config()
        self.memory_manager = MemoryManager(offsets, client_data, buttons_data)
        self.memory_manager.config = self.config  # Pass configuration to MemoryManager
        self.is_running, self.stop_event = False, threading.Event()
        self.trigger_active = False
        self.toggle_state = False 
        self.update_config(self.config)

        # Initialize configuration settings
        self.load_configuration()

        # Setup listeners
        self.keyboard_listener = KeyboardListener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.mouse_listener = MouseListener(on_click=self.on_mouse_click)
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def load_configuration(self) -> None:
        """Load and apply configuration settings."""
        settings = self.config['Trigger']
        self.trigger_key = settings['TriggerKey']
        self.toggle_mode = settings['ToggleMode']
        self.shot_delay_min = settings['ShotDelayMin']
        self.shot_delay_max = settings['ShotDelayMax']
        self.post_shot_delay = settings['PostShotDelay']
        self.attack_on_teammates = settings['AttackOnTeammates']
        
        # Determine if the trigger key is a mouse button
        self.mouse_button_map = {
            "mouse3": Button.middle,
            "mouse4": Button.x1,
            "mouse5": Button.x2,
        }

        # Check if the trigger key is a mouse button
        self.is_mouse_trigger = self.trigger_key in self.mouse_button_map

    def update_config(self, config):
        """Update the configuration settings."""
        self.config = config
        self.memory_manager.config = self.config
        self.load_configuration()

    def play_toggle_sound(self, state: bool) -> None:
        """Play a sound when the toggle key is pressed."""
        try:
            if state:
                # Sound for activation: frequency 1000 Hz, duration 200 ms
                winsound.Beep(1000, 200)
            else:
                # Sound for deactivation: frequency 500 Hz, duration 200 ms
                winsound.Beep(500, 200)
        except Exception as e:
            logger.error("Error playing toggle sound: {e}")

    def on_key_press(self, key) -> None:
        """Handle key press events."""
        if not self.is_mouse_trigger:
            try:
                # Check if the key pressed is the trigger key
                if hasattr(key, 'char') and key.char == self.trigger_key:
                    if self.toggle_mode:
                        self.toggle_state = not self.toggle_state
                        self.play_toggle_sound(self.toggle_state)
                    else:
                        self.trigger_active = True
            except AttributeError:
                pass

    def on_key_release(self, key) -> None:
        """Handle key release events."""
        if not self.is_mouse_trigger and not self.toggle_mode:
            try:
                if hasattr(key, 'char') and key.char == self.trigger_key:
                    self.trigger_active = False
            except AttributeError:
                pass

    def on_mouse_click(self, x, y, button, pressed) -> None:
        """Handle mouse click events."""
        if not self.is_mouse_trigger:
            return

        expected_btn = self.mouse_button_map.get(self.trigger_key)
        if button == expected_btn:
            if self.toggle_mode and pressed:
                self.toggle_state = not self.toggle_state
                self.play_toggle_sound(self.toggle_state)
            else:
                self.trigger_active = pressed

    def should_trigger(self, entity_team: int, player_team: int, entity_health: int) -> bool:
        """Determine if the bot should fire."""
        return (self.attack_on_teammates or entity_team != player_team) and entity_health > 0

    def start(self) -> None:
        """Start the TriggerBot."""
        if not self.memory_manager.initialize():
            return
        # Set the running flag to True and log that the TriggerBot has started
        self.is_running = True
        logger.info("TriggerBot started.")

        # Define local variables for utility functions
        is_game_active = Utility.is_game_active
        sleep = time.sleep

        while not self.stop_event.is_set():
            try:
                # Check if the game is active
                if not is_game_active():
                    sleep(MAIN_LOOP_SLEEP)
                    continue

                if self.toggle_mode:
                    if self.toggle_state:
                        data = self.memory_manager.get_fire_logic_data()
                        if data and self.should_trigger(data["entity_team"], data["player_team"], data["entity_health"]):
                            sleep(random.uniform(self.shot_delay_min, self.shot_delay_max))
                            mouse.click(Button.left)
                            sleep(self.post_shot_delay)
                else:
                    if self.is_mouse_trigger and self.trigger_active:
                        data = self.memory_manager.get_fire_logic_data()
                        if data and self.should_trigger(data["entity_team"], data["player_team"], data["entity_health"]):
                            sleep(random.uniform(self.shot_delay_min, self.shot_delay_max))
                            mouse.click(Button.left)
                            sleep(self.post_shot_delay)
                    elif not self.is_mouse_trigger and keyboard.is_pressed(self.trigger_key):
                        data = self.memory_manager.get_fire_logic_data()
                        if data and self.should_trigger(data["entity_team"], data["player_team"], data["entity_health"]):
                            sleep(random.uniform(self.shot_delay_min, self.shot_delay_max))
                            mouse.click(Button.left)
                            sleep(self.post_shot_delay)

                sleep(MAIN_LOOP_SLEEP)
            except KeyboardInterrupt:
                logger.info("TriggerBot stopped by user.")
                self.stop()
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}", exc_info=True)

    def stop(self) -> None:
        """
        Stops the TriggerBot and cleans up resources.
        Also stops the keyboard and mouse listeners.
        """
        # Set the running flag to False and signal the stop event
        self.is_running = False
        self.stop_event.set()
        # Stop the keyboard and mouse listeners
        if self.keyboard_listener.running:
            self.keyboard_listener.stop()
        if self.mouse_listener.running:
            self.mouse_listener.stop()
        # Log that the TriggerBot has stopped
        logger.info(f"TriggerBot stopped.")