from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QMainWindow, QPushButton, QLabel, QLineEdit, QTextEdit, QCheckBox, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QFormLayout, QTabWidget
from PyQt6.QtGui import QIcon, QShortcut, QKeySequence
from watchdog.observers import Observer
from datetime import datetime
from packaging import version
from classes.utility import Utility
from classes.trigger_bot import CS2TriggerBot
from classes.config_manager import ConfigManager
from classes.file_watcher import ConfigFileChangeHandler
from classes.logger import Logger
import threading, os, requests

# Initialize the logger for consistent logging
logger = Logger.get_logger()

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initialize the main application window and setup UI components.
        """
        super().__init__()
        self.setWindowTitle("CS2 TriggerBot | github.com/Jesewe/cs2-triggerbot")
        self.setFixedSize(700, 400)

        # Apply custom styles for the UI
        self.setStyleSheet("""
            QMainWindow { background-color: #1A1A1A; color: #E0E0E0; font-family: Arial; font-size: 15px; }
            QLabel { color: #F0F0F0; font-weight: bold; }
            QLineEdit, QComboBox { background-color: #2C2C2C; color: #E0E0E0; border: 1px solid #444444; padding: 5px; border-radius: 5px; }
            QTextEdit { background-color: #2C2C2C;  color: #E0E0E0;  border: 1px solid #444444;  border-radius: 5px; padding: 10px; font-family: Consolas, monospace; font-size: 14px; }
            QTextEdit:focus { border: 1px solid #D5006D; }
            QPushButton { background-color: #333333; color: #D5006D; font-weight: bold; padding: 8px 15px; border-radius: 15px; border: 1px solid #555555; }
            QPushButton:hover { background-color: #444444; }
            QTabWidget::pane { border: 1px solid #444444; background-color: #1A1A1A; border-radius: 5px; }
            QTabBar::tab { background-color: #2C2C2C; color: #E0E0E0; padding: 8px 15px; border: 1px solid #444444; border-top-left-radius: 5px; border-top-right-radius: 5px; margin: 2px; font-weight: bold; }
            QTabBar::tab:selected { background-color: #444444; color: #D5006D; border-bottom: 2px solid #D5006D; }
            QTabBar::tab:hover { background-color: #333333; }
        """)

        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.info("Icon not found, skipping.")

        # Initialize layout and tabs
        self.main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Fetch offsets and initialize TriggerBot
        offsets, client_data = Utility.fetch_offsets()
        if offsets is None or client_data is None:
            QMessageBox.warning(self, "Offsets Fetch Error", "Failed to fetch offsets from the server.")
            offsets, client_data = {}, {}

        self.bot = CS2TriggerBot(offsets, client_data)

        # Initialize the tabs
        self.init_home_tab()
        self.init_general_settings_tab()
        self.init_logs_tab()
        self.init_faq_tab()

        self.main_layout.addWidget(self.tabs)
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # Setup log file monitoring
        self.last_log_position = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_log_output)
        self.timer.start(1000)  # Update logs every second

        # Initialize file watcher for config updates
        self.init_config_watcher()

        # Initialize keyboard shortcuts for starting/stopping the bot
        self.init_shortcuts()

    def init_home_tab(self):
        """
        Setup the Home tab with basic information, bot controls, and status display.
        """
        home_tab = QWidget()
        layout = QVBoxLayout()

        # Application name
        self.name_app = QLabel(f"CS2 TriggerBot {CS2TriggerBot.VERSION}")
        self.name_app.setStyleSheet("color: #D5006D; font-size: 18px; font-weight: bold;")

        # Update info
        self.update_info = QLabel(self)
        self.check_for_updates(self.bot.VERSION)

        # Status label
        self.status_label = QLabel("Bot Status: Stopped")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        # Last offsets update
        self.last_update_label = QLabel("Last offsets update: Fetching...")
        self.last_update_label.setStyleSheet("font-size: 13px; font-style: italic;")
        self.fetch_last_offset_update()

        # Quick start guide
        quick_start_label = QLabel("Quick Start Guide")
        quick_start_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #D5006D;")
        quick_start_text = QLabel(
            "1. Open CS2 game and ensure it’s running.\n"
            "2. Configure trigger key and delays in 'General Settings'.\n"
            "3. Press 'Start Bot' to activate.\n"
            "4. Monitor bot status and logs in the 'Logs' tab."
        )
        quick_start_text.setWordWrap(True)
        quick_start_text.setStyleSheet("font-size: 13px;")

        # Start/Stop buttons
        self.start_button = QPushButton("Start Bot")
        self.stop_button = QPushButton("Stop Bot")
        self.start_button.clicked.connect(self.start_bot)
        self.stop_button.clicked.connect(self.stop_bot)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.setSpacing(20)

        # Add components to the layout
        layout.addWidget(self.name_app)
        layout.addWidget(self.update_info)
        layout.addWidget(quick_start_label)
        layout.addWidget(quick_start_text)
        layout.addWidget(self.status_label)
        layout.addWidget(self.last_update_label)
        layout.addLayout(buttons_layout)
        home_tab.setLayout(layout)
        self.tabs.addTab(home_tab, "Home")

    def init_general_settings_tab(self):
        """
        Setup the General Settings tab for configuring the bot.
        """
        general_settings_tab = QWidget()
        form_layout = QFormLayout()

        # Input fields for configuration
        self.trigger_key_input = QLineEdit(self.bot.config['Settings']['TriggerKey'])
        self.min_delay_input = QLineEdit(str(self.bot.config['Settings']['ShotDelayMin']), self)
        self.max_delay_input = QLineEdit(str(self.bot.config['Settings']['ShotDelayMax']), self)
        self.post_shot_delay_input = QLineEdit(str(self.bot.config['Settings'].get('PostShotDelay', 0.1)), self)
        self.attack_teammates_checkbox = QCheckBox("Attack Teammates")
        self.attack_teammates_checkbox.setChecked(self.bot.config['Settings']['AttackOnTeammates'])

        # Add fields to the form layout
        form_layout.addRow("Trigger Key:", self.trigger_key_input)
        form_layout.addRow("Min Shot Delay:", self.min_delay_input)
        form_layout.addRow("Max Shot Delay:", self.max_delay_input)
        form_layout.addRow("Post Shot Delay:", self.post_shot_delay_input)
        form_layout.addRow(self.attack_teammates_checkbox)

        # Save button
        save_button = QPushButton("Save Config")
        save_button.clicked.connect(self.save_general_settings)
        form_layout.addRow(save_button)

        general_settings_tab.setLayout(form_layout)
        self.tabs.addTab(general_settings_tab, "General Settings")

    def init_logs_tab(self):
        """
        Setup the Logs tab to display application logs.
        """
        logs_tab = QWidget()
        layout = QVBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        logs_tab.setLayout(layout)
        self.tabs.addTab(logs_tab, "Logs")

    def init_faq_tab(self):
        """
        Setup the FAQs tab to provide help and common questions/answers.
        """
        faq_tab = QWidget()
        layout = QVBoxLayout()

        faqs_content = """
        <h3 style="color:#D5006D;">Frequently Asked Questions</h3>
        <p><b>Q: What is a <span style="color:#BB86FC;">TriggerBot</span>?</b></p>
        <p>A: A <span style="color:#BB86FC;">TriggerBot</span> is a software tool that automatically shoots when the crosshair is over an enemy in a game.</p>
        
        <p><b>Q: Is this tool safe to use?</b></p>
        <p>A: This tool is for educational purposes only. Use it at your own risk as it may violate the game's <span style="color:#BB86FC;">terms of service</span>.</p>
        
        <p><b>Q: How do I start the <span style="color:#BB86FC;">TriggerBot</span>?</b></p>
        <p>A: Go to the 'Home' tab and click 'Start Bot' after ensuring the game is running and properly configured.</p>
        
        <p><b>Q: How can I update the <span style="color:#BB86FC;">offsets</span>?</b></p>
        <p>A: <span style="color:#BB86FC;">Offsets</span> are fetched automatically from the server. Check the 'Home' tab for the last update timestamp.</p>
        
        <p><b>Q: Can I customize the bot's behavior?</b></p>
        <p>A: Yes, use the 'General Settings' tab to adjust <span style="color:#BB86FC;">key configurations</span>, delays, and teammate attack settings.</p>
        
        <p><b>Q: I found a bug, where can I report it?</b></p>
        <p>A: You can report bugs by opening an issue on our <a style="color: #BB86FC;">GitHub Issues page</a>. Please include details about the bug and steps to reproduce it.</p>
        """

        faqs_widget = QTextEdit()
        faqs_widget.setHtml(faqs_content)
        faqs_widget.setReadOnly(True)
        layout.addWidget(faqs_widget)

        faq_tab.setLayout(layout)
        self.tabs.addTab(faq_tab, "FAQs")

    def init_config_watcher(self):
        """
        Initializes a file watcher to monitor changes in the configuration file.
        Automatically updates the bot's configuration when the file changes.
        """
        event_handler = ConfigFileChangeHandler(self.bot)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=ConfigManager.CONFIG_DIRECTORY, recursive=False)
        self.observer.start()

    def init_shortcuts(self):
        """
        Sets up keyboard shortcuts for quick access to start and stop bot functions.
        - Ctrl+S: Start the bot
        - Ctrl+Q: Stop the bot
        """
        self.start_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.start_shortcut.activated.connect(self.start_bot)

        self.stop_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.stop_shortcut.activated.connect(self.stop_bot)

    def closeEvent(self, event):
        """
        Handles application close event to ensure resources are cleaned up:
        - Stops the file watcher.
        - Stops the bot if it is running.
        """
        self.observer.stop()
        self.bot.stop()
        self.observer.join()
        event.accept()

    def check_for_updates(self, current_version):
        """
        Checks the GitHub repository for the latest version of the software.
        Compares the current version with the latest version and displays a message if an update is available.
        """
        try:
            response = requests.get("https://api.github.com/repos/Jesewe/cs2-triggerbot/tags")
            response.raise_for_status()
            latest_version = response.json()[0]["name"]

            if version.parse(latest_version) > version.parse(current_version):
                self.update_info.setText(f"New version available: {latest_version}. Please update for the latest fixes and features.")
                self.update_info.setStyleSheet("color: #BB86FC;")
            elif version.parse(current_version) > version.parse(latest_version):
                self.update_info.setText("Developer version: You are using a pre-release or developer version.")
                self.update_info.setStyleSheet("color: #F1C40F;")
            else:
                self.update_info.setText("You are using the latest version.")
                self.update_info.setStyleSheet("color: #df73ff;")
        except Exception as e:
            self.update_info.setText(f"Error checking for updates. {e}")
            self.update_info.setStyleSheet("color: red;")

    def fetch_last_offset_update(self):
        """
        Fetches the timestamp of the latest commit to the offsets repository.
        Displays the timestamp in the UI or an error message if the fetch fails.
        """
        try:
            response = requests.get("https://api.github.com/repos/a2x/cs2-dumper/commits/main")
            response.raise_for_status()
            commit_data = response.json()
            commit_timestamp = commit_data["commit"]["committer"]["date"]

            last_update_dt = datetime.fromisoformat(commit_timestamp.replace("Z", "+00:00"))
            formatted_timestamp = last_update_dt.strftime("%m/%d/%Y %H:%M:%S")
            
            self.last_update_label.setText(f"Last offsets update: {formatted_timestamp} (UTC)")
            self.last_update_label.setStyleSheet("color: orange; font-weight: bold;")
            logger.info(f"Offsets last updated: {formatted_timestamp}")
        except Exception as e:
            self.last_update_label.setText("Error fetching last offsets update.")
            self.last_update_label.setStyleSheet("color: orange; font-weight: bold;")
            logger.error(f"Offset update fetch failed: {e}")

    def start_bot(self):
        """
        Starts the bot if it is not already running:
        - Validates user inputs for the bot's configuration.
        - Ensures the game process (cs2.exe) is running.
        - Launches the bot in a separate thread.
        """
        if self.bot.is_running:
            QMessageBox.warning(self, "Bot started", "The bot is already running.")
            return

        if not self.bot.is_game_running():
            QMessageBox.critical(self, "The game is not running", "Could not find cs2.exe process. Make sure the game is running.")
            return

        try:
            self.validate_inputs()

            # Clear the stop event to ensure the bot runs
            self.bot.stop_event.clear()
            
            # Start the bot in a separate thread
            self.bot_thread = threading.Thread(target=self.bot.start, daemon=True)
            self.bot_thread.start()

            self.status_label.setText("Bot Status: Running")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        except ValueError as ve:
            QMessageBox.critical(self, "Invalid Input", str(ve))

    def stop_bot(self):
        """
        Stops the bot if it is currently running:
        - Signals the bot's stop event to terminate its main loop.
        - Waits for the bot's thread to terminate and updates the UI.
        """
        if self.bot.is_running:
            self.bot.stop()
            if self.bot_thread is not None:
                self.bot_thread.join(timeout=2)
                if self.bot_thread.is_alive():
                    logger.warning("Bot thread did not terminate cleanly.")
                self.bot_thread = None

            self.status_label.setText("Bot Status: Stopped")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            QMessageBox.warning(self, "Bot has not been started", "The bot is not running.")

    def save_general_settings(self):
        """
        Saves the user's changes to the bot's configuration:
        - Updates the bot's configuration with new values.
        - Persists the updated configuration using the ConfigManager.
        """
        self.bot.config['Settings']['TriggerKey'] = self.trigger_key_input.text()
        self.bot.config['Settings']['AttackOnTeammates'] = self.attack_teammates_checkbox.isChecked()
        self.bot.config['Settings']['ShotDelayMin'] = float(self.min_delay_input.text())
        self.bot.config['Settings']['ShotDelayMax'] = float(self.max_delay_input.text())
        self.bot.config['Settings']['PostShotDelay'] = float(self.post_shot_delay_input.text())
        ConfigManager.save_config(self.bot.config)
        self.bot.update_config(self.bot.config)

    def validate_inputs(self):
        """
        Validates user input fields in the General Settings tab.
        Ensures all required fields have valid values.
        """
        try:
            trigger_key = self.trigger_key_input.text()
            if not trigger_key:
                raise ValueError("Trigger key cannot be empty.")

            min_delay = float(self.min_delay_input.text())
            max_delay = float(self.max_delay_input.text())
            post_delay = float(self.post_shot_delay_input.text())

            if min_delay < 0 or max_delay < 0 or post_delay < 0:
                raise ValueError("Delay values must be non-negative.")
            if min_delay > max_delay:
                raise ValueError("Minimum delay cannot be greater than maximum delay.")
        except ValueError as e:
            raise ValueError(f"Invalid input: {e}")

    def update_log_output(self):
        """
        Periodically updates the Logs tab with new log entries from the log file.
        Appends new log entries since the last read position to the log display.
        """
        try:
            with open(Logger.LOG_FILE, 'r') as log_file:
                log_file.seek(self.last_log_position)
                new_logs = log_file.read()
                self.last_log_position = log_file.tell()

                if new_logs:
                    self.log_output.append(new_logs)
                    self.log_output.ensureCursorVisible()
        except Exception as e:
            self.log_output.append(f"Error reading log file: {e}")
            self.log_output.ensureCursorVisible()