import sys
import logging
import os
import json
import pymem
import pymem.process
import keyboard
import time
import threading
import psutil
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QTextEdit, QCheckBox, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QIcon
from pynput.mouse import Controller, Button, Listener
from requests import get
from random import uniform
from win32gui import GetWindowText, GetForegroundWindow
from packaging import version
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Initialize mouse controller for trigger actions
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

    _config_cache = None  # Singleton cache to avoid redundant reads

    @classmethod
    def load_config(cls):
        """Load configuration, filling in any missing keys with defaults."""
        if cls._config_cache is not None:
            return cls._config_cache

        # Ensure the config directory exists
        if not os.path.exists(cls.CONFIG_DIRECTORY):
            os.makedirs(cls.CONFIG_DIRECTORY)

        # Load the configuration file or create it if it doesn't exist
        if not os.path.exists(cls.CONFIG_FILE):
            logging.info("config.json not found, creating a default configuration.")
            cls.save_config(cls.DEFAULT_CONFIG)
            cls._config_cache = cls.DEFAULT_CONFIG
        else:
            # Load the existing configuration
            try:
                with open(cls.CONFIG_FILE, 'r') as config_file:
                    cls._config_cache = json.load(config_file)
                    logging.info("Loaded configuration.")
            except (json.JSONDecodeError, IOError) as e:
                cls._config_cache = cls.DEFAULT_CONFIG

            # Add missing keys from the default configuration
            updated = False
            for key, default_value in cls.DEFAULT_CONFIG.items():
                if key not in cls._config_cache:
                    cls._config_cache[key] = default_value
                    updated = True
                elif isinstance(default_value, dict):
                    for sub_key, sub_value in default_value.items():
                        if sub_key not in cls._config_cache[key]:
                            cls._config_cache[key][sub_key] = sub_value
                            updated = True

            # Save the updated config if any missing keys were added
            if updated:
                cls.save_config(cls._config_cache)

        return cls._config_cache

    @classmethod
    def save_config(cls, config):
        cls._config_cache = config  # Update the cache
        with open(cls.CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file, indent=4)
            logging.info(f"Saved configuration.")

class ConfigFileChangeHandler(FileSystemEventHandler):
    def __init__(self, bot):
        self.bot = bot

    def on_modified(self, event):
        if event.src_path == ConfigManager.CONFIG_FILE:
            new_config = ConfigManager.load_config()
            self.bot.update_config(new_config)

class Utility:
    CACHE_DIRECTORY = ConfigManager.CONFIG_DIRECTORY
    CACHE_FILE = os.path.join(CACHE_DIRECTORY, 'offsets_cache.json')

    @staticmethod
    def fetch_offsets():
        try:
            response_offset = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json")
            response_client = get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json")

            if response_offset.status_code != 200 or response_client.status_code != 200:
                logging.error(f"Failed to fetch offsets from server.")
                return None, None

            offset = response_offset.json()
            client = response_client.json()

            if os.path.exists(Utility.CACHE_FILE):
                with open(Utility.CACHE_FILE, 'r') as f:
                    cached_data = json.load(f)

                if cached_data.get('offsets') != offset or cached_data.get('client') != client:
                    logging.info(f"Offsets have changed, updating cache...")
                    with open(Utility.CACHE_FILE, 'w') as f:
                        json.dump({'offsets': offset, 'client': client}, f)
                else:
                    logging.info(f"Using cached offsets.")
                    return cached_data['offsets'], cached_data['client']
            else:
                os.makedirs(Utility.CACHE_DIRECTORY, exist_ok=True)
                with open(Utility.CACHE_FILE, 'w') as f:
                    json.dump({'offsets': offset, 'client': client}, f)

            return offset, client
        except Exception as e:
            logging.error(f"Failed to fetch offsets: {e}")
            return None, None

class CS2TriggerBot:
    VERSION = "v1.1.3"

    def __init__(self, offsets, client_data):
        self.config = ConfigManager.load_config()
        self.offsets = offsets
        self.client_data = client_data
        self.pm = None
        self.client_base = None
        self.dwEntityList = None
        self.dwLocalPlayerPawn = None
        self.m_iHealth = None
        self.m_iTeamNum = None
        self.m_iIDEntIndex = None
        self.is_running = False
        self.stop_event = threading.Event()
        self.trigger_key = self.config['Settings']['TriggerKey']
        self.shot_delay_min = self.config['Settings']['ShotDelayMin']
        self.shot_delay_max = self.config['Settings']['ShotDelayMax']
        self.attack_on_teammates = self.config['Settings']['AttackOnTeammates']
        self.initialize_offsets()

    def initialize_offsets(self):
        self.dwEntityList = self.offsets["client.dll"]["dwEntityList"]
        self.dwLocalPlayerPawn = self.offsets["client.dll"]["dwLocalPlayerPawn"]
        self.m_iHealth = self.client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iHealth"]
        self.m_iTeamNum = self.client_data["client.dll"]["classes"]["C_BaseEntity"]["fields"]["m_iTeamNum"]
        self.m_iIDEntIndex = self.client_data["client.dll"]["classes"]["C_CSPlayerPawnBase"]["fields"]["m_iIDEntIndex"]

    def update_config(self, config):
        self.config = config
        self.trigger_key = self.config['Settings']['TriggerKey']
        self.shot_delay_min = self.config['Settings']['ShotDelayMin']
        self.shot_delay_max = self.config['Settings']['ShotDelayMax']
        self.attack_on_teammates = self.config['Settings']['AttackOnTeammates']

    @staticmethod
    def is_game_active():
        return GetWindowText(GetForegroundWindow()) == "Counter-Strike 2"
    
    @staticmethod
    def is_game_running():
        """Check if the cs2.exe process is running."""
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if proc.info['name'] == 'cs2.exe':
                return True
        return False

    def initialize_pymem(self):
        try:
            self.pm = pymem.Pymem("cs2.exe")
            logging.info(f"Successfully attached to cs2.exe process.")
        except pymem.exception.ProcessNotFound:
            logging.error(f"Could not find cs2.exe process. Please make sure the game is running.")
        except pymem.exception.PymemError as e:
            logging.error(f"Pymem encountered an error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during Pymem initialization: {e}")
        return self.pm is not None

    def get_client_module(self):
        try:
            if self.client_base is None:
                client_module = pymem.process.module_from_name(self.pm.process_handle, "client.dll")
                if not client_module:
                    raise pymem.exception.ModuleNotFoundError("client.dll not found")
                self.client_base = client_module.lpBaseOfDll
        except pymem.exception.ModuleNotFoundError as e:
            logging.error(f"Error: {e}. Ensure client.dll is loaded.")
        except Exception as e:
            logging.error(f"Unexpected error retrieving client module: {e}")
        return self.client_base is not None

    def get_entity(self, index):
        try:
            ent_list = self.pm.read_longlong(self.client_base + self.dwEntityList)
            ent_entry = self.pm.read_longlong(ent_list + 0x8 * (index >> 9) + 0x10)
            return self.pm.read_longlong(ent_entry + 120 * (index & 0x1FF))
        except Exception as e:
            logging.error(f"Error reading entity: {e}")
            return None

    def should_trigger(self, entity_team, player_team, entity_health):
        if self.attack_on_teammates:
            return entity_health > 0
        return entity_team != player_team and entity_health > 0

    def start(self):
        if not self.initialize_pymem():
            return

        if not self.get_client_module():
            return

        self.is_running = True

        while not self.stop_event.is_set():
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
                logging.info(f"TriggerBot stopped by user.")
                self.stop()
            except Exception as e:
                logging.error(f"Unexpected error: {e}")

    def stop(self):
        self.is_running = False
        self.stop_event.set()
        logging.info("TriggerBot stopped.")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"CS2 TriggerBot | github.com/Jesewe/cs2-triggerbot")
        self.setGeometry(100, 100, 700, 500)
        self.setFixedSize(700, 500)
        self.setStyleSheet("background-color: #111111; color: #f0f0f0; font-family: Arial; font-size: 16px; font-weight: bold;")

        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logging.warning("Icon not found, skipping.")

        offsets, client_data = Utility.fetch_offsets()
        if offsets is None or client_data is None:
            QMessageBox.warning(self, "Offsets Fetch Error", "Failed to fetch offsets from the server. The bot may not work correctly.")
            offsets = {}  # Initialize empty offsets as a fallback
            client_data = {}  # Initialize empty client data as a fallback

        self.bot = CS2TriggerBot(offsets, client_data)

        main_layout = QVBoxLayout()

        self.name_app = QLabel(f"CS2 TriggerBot {CS2TriggerBot.VERSION}", self)
        self.name_app.setStyleSheet("color: #D5006D;")
        
        self.update_info = QLabel(self)
        self.check_for_updates(self.bot.VERSION)

        self.trigger_key_label = QLabel("Trigger Key:", self)
        self.trigger_key_input = QLineEdit(self.bot.config['Settings']['TriggerKey'], self)
        self.trigger_key_input.setStyleSheet("background-color: #222222; color: white;")

        self.min_delay_label = QLabel("Min Shot Delay:", self)
        self.min_delay_input = QLineEdit(str(self.bot.config['Settings']['ShotDelayMin']), self)
        self.min_delay_input.setStyleSheet("background-color: #222222; color: white;")

        self.max_delay_label = QLabel("Max Shot Delay:", self)
        self.max_delay_input = QLineEdit(str(self.bot.config['Settings']['ShotDelayMax']), self)
        self.max_delay_input.setStyleSheet("background-color: #222222; color: white;")

        self.attack_teammates_checkbox = QCheckBox("Attack Teammates", self)
        self.attack_teammates_checkbox.setChecked(self.bot.config['Settings']['AttackOnTeammates'])
        self.attack_teammates_checkbox.setStyleSheet("color: white;")

        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #222222; color: white; height: 80px;")

        buttons_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Bot", self)
        self.start_button.setStyleSheet("""
    QPushButton {
        background-color: #1E1E1E; 
        color: #D5006D; 
        border-radius: 15px;}
    QPushButton:pressed {
        background-color: #161616;}""")
        buttons_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Bot", self)
        self.stop_button.setStyleSheet("""
    QPushButton {
        background-color: #1E1E1E; 
        color: #D5006D; 
        border-radius: 15px;}
    QPushButton:pressed {
        background-color: #161616;}""")
        buttons_layout.addWidget(self.stop_button)

        self.save_button = QPushButton("Save Config", self)
        self.save_button.setStyleSheet("""
    QPushButton {
        background-color: #1E1E1E; 
        color: #D5006D; 
        border-radius: 15px;}
    QPushButton:pressed {
        background-color: #161616;}""")

        main_layout.addWidget(self.name_app)
        main_layout.addWidget(self.update_info)
        main_layout.addWidget(self.trigger_key_label)
        main_layout.addWidget(self.trigger_key_input)
        main_layout.addWidget(self.min_delay_label)
        main_layout.addWidget(self.min_delay_input)
        main_layout.addWidget(self.max_delay_label)
        main_layout.addWidget(self.max_delay_input)
        main_layout.addWidget(self.attack_teammates_checkbox)
        main_layout.addWidget(self.save_button)
        main_layout.addWidget(self.log_output)
        main_layout.addLayout(buttons_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.start_button.clicked.connect(self.start_bot)
        self.stop_button.clicked.connect(self.stop_bot)
        self.save_button.clicked.connect(self.save_config)

        self.last_log_position = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log_output)
        self.timer.start(1000)

        self.init_config_watcher()

    def init_config_watcher(self):
        event_handler = ConfigFileChangeHandler(self.bot)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=ConfigManager.CONFIG_DIRECTORY, recursive=False)
        self.observer.start()

    def closeEvent(self, event):
        self.observer.stop()
        self.bot.stop()
        self.observer.join()
        event.accept()

    def check_for_updates(self, current_version):
        try:
            response = get("https://api.github.com/repos/Jesewe/cs2-triggerbot/tags")
            response.raise_for_status()
            latest_version = response.json()[0]["name"]
            if version.parse(latest_version) > version.parse(current_version):
                self.update_info.setText(f"New version available: {latest_version}. Please update for the latest fixes and features.")
                self.update_info.setStyleSheet("color: #BB86FC;")
                QMessageBox.information(self, "Update Available", f"A new version {latest_version} is available. \nPlease update to get the latest features and fixes.")
            elif version.parse(current_version) > version.parse(latest_version):
                self.update_info.setText("Developer version: You are using a pre-release or developer version.")
                self.update_info.setStyleSheet("color: #F1C40F;")
            else:
                self.update_info.setText("You are using the latest version.")
                self.update_info.setStyleSheet("color: #df73ff;")
        except Exception as e:
            self.update_info.setText("Error checking for updates.")
            self.update_info.setStyleSheet("color: red;")

    def start_bot(self):
        """Handle start bot action with button state control."""
        if self.bot.is_running:
            QMessageBox.warning(self, "Bot Running", "The bot is already running.")
            return
        
        if not self.bot.is_game_running():
            QMessageBox.critical(self, "Game Not Running", "Could not find cs2.exe process. Make sure the game is running.")
            return

        try:
            self.validate_inputs()

            self.bot.stop_event.clear()
            
            # Start bot in a separate thread
            self.bot_thread = threading.Thread(target=self.bot.start, daemon=True)
            self.bot_thread.start()
        except ValueError as ve:
            QMessageBox.critical(self, "Invalid Input", str(ve))
        
    def stop_bot(self):
        """Handle stop bot action with thread cleanup."""
        if self.bot.is_running:
            self.bot.stop()
            if self.bot_thread is not None:
                self.bot_thread.join()
                self.bot_thread = None
        else:
            QMessageBox.warning(self, "Bot Not Running", "The bot is not running.")

    def save_config(self):
        """Handle config saving logic and reinitialize bot if needed."""
        try:
            self.validate_inputs()
            bot_was_running = self.bot.is_running

            if bot_was_running:
                self.stop_bot()

            self.update_bot_config_from_ui()

            ConfigManager.save_config(self.bot.config)

            if bot_was_running:
                self.start_bot()
        except ValueError as ve:
            QMessageBox.critical(self, "Invalid Input", str(ve))

    def validate_inputs(self):
        """Ensure inputs for delay and trigger key are valid."""
        try:
            min_delay = float(self.min_delay_input.text())
            max_delay = float(self.max_delay_input.text())

            if min_delay <= 0 or max_delay <= 0 or min_delay > max_delay:
                raise ValueError("Shot delay values must be positive and min should be less than max.")
        except ValueError:
            raise ValueError("Invalid shot delay values.")

        trigger_key = self.trigger_key_input.text()
        if not trigger_key:
            raise ValueError("Trigger key cannot be empty.")

    def update_bot_config_from_ui(self):
        """Update bot configuration based on the current UI values."""
        self.bot.config['Settings']['TriggerKey'] = self.trigger_key_input.text()
        self.bot.config['Settings']['ShotDelayMin'] = float(self.min_delay_input.text())
        self.bot.config['Settings']['ShotDelayMax'] = float(self.max_delay_input.text())
        self.bot.config['Settings']['AttackOnTeammates'] = self.attack_teammates_checkbox.isChecked()

    def update_log_output(self):
        """Append new log entries to the log_output widget."""
        try:
            with open(Logger.LOG_FILE, 'r') as log_file:
                log_file.seek(self.last_log_position)  # Start reading from the last position
                new_logs = log_file.read()
                self.last_log_position = log_file.tell()  # Update the last position to the end of the file

                if new_logs:
                    self.log_output.append(new_logs)
                    self.log_output.ensureCursorVisible()  # Ensure the latest logs are visible
        except Exception as e:
            self.log_output.append(f"Error reading log file: {e}")
            self.log_output.ensureCursorVisible()

if __name__ == '__main__':
    Logger.setup_logging()
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())