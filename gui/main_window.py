import os
import threading

from PyQt6.QtCore import Qt, QTimer, QUrl, QSize
from PyQt6.QtWidgets import (QMainWindow, QPushButton, QLabel, QLineEdit, QTextEdit,
                             QCheckBox, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox,
                             QFormLayout, QTabWidget, QSpacerItem, QSizePolicy)
from PyQt6.QtGui import QIcon, QDesktopServices

from watchdog.observers import Observer

from classes.utility import Utility
from classes.trigger_bot import CS2TriggerBot
from classes.config_manager import ConfigManager
from classes.file_watcher import ConfigFileChangeHandler
from classes.logger import Logger

from gui.home_tab import init_home_tab
from gui.general_settings_tab import init_general_settings_tab
from gui.logs_tab import init_logs_tab
from gui.faq_tab import init_faq_tab

# Cache the logger instance
logger = Logger.get_logger()

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initialize the main application window and setup UI components.
        """
        super().__init__()

        self.repo_url = "github.com/Jesewe/cs2-triggerbot"
        self.setWindowTitle(f"CS2 TriggerBot | {self.repo_url}")
        self.setFixedSize(700, 500)

        # Load and apply custom styles from external stylesheet.
        self.apply_stylesheet(Utility.resource_path('src/styles.css'))

        # Set application icon if available.
        self.set_app_icon(Utility.resource_path('src/img/icon.png'))

        # Create main layout with tabs.
        self.main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Fetch offsets and initialize the TriggerBot.
        offsets, client_data = self.fetch_offsets_or_warn()
        self.bot = CS2TriggerBot(offsets, client_data)

        # Build tabs using functions from separate modules.
        init_home_tab(self)
        init_general_settings_tab(self)
        init_logs_tab(self)
        init_faq_tab(self)

        # Build the top section (header) with app name and icon buttons.
        self.top_layout = self.build_top_layout()

        self.main_layout.addLayout(self.top_layout)
        self.main_layout.addWidget(self.tabs)
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # Setup periodic log updates.
        self.last_log_position = 0
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.update_log_output)
        self.log_timer.start(1000)  # Update logs every second

        # Initialize file watcher for configuration changes.
        self.init_config_watcher()

    def apply_stylesheet(self, stylesheet_path):
        """Load and apply the stylesheet if available."""
        try:
            with open(stylesheet_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            logger.error("Failed to load stylesheet: %s", e)

    def set_app_icon(self, icon_path):
        """Set the application icon if the file exists."""
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            logger.info("Icon not found at %s, skipping.", icon_path)

    def fetch_offsets_or_warn(self):
        """Attempt to fetch offsets; warn the user and return empty dictionaries on failure."""
        try:
            offsets, client_data = Utility.fetch_offsets()
            if offsets is None or client_data is None:
                raise ValueError("Failed to fetch offsets from the server.")
            return offsets, client_data
        except Exception as e:
            QMessageBox.warning(self, "Offsets Fetch Error", str(e))
            return {}, {}

    def build_top_layout(self):
        """Builds the top layout with the app title and icon buttons."""
        top_layout = QHBoxLayout()

        # Application title label.
        name_app = QLabel(f"CS2 TriggerBot {CS2TriggerBot.VERSION}")
        name_app.setStyleSheet("color: #D5006D; font-size: 22px; font-weight: bold;")

        # Create icon buttons.
        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        icon_layout.addWidget(self.create_icon_button('src/img/telegram_icon.png',
                                                        "Join our Telegram channel",
                                                        "https://t.me/cs2_jesewe"))
        icon_layout.addWidget(self.create_icon_button('src/img/github_icon.png',
                                                        "Visit our GitHub repository",
                                                        "https://github.com/Jesewe/cs2-triggerbot"))

        # Check for updates.
        update_url = Utility.check_for_updates(CS2TriggerBot.VERSION)
        if update_url:
            update_btn = self.create_icon_button('src/img/update_icon.png',
                                                 "New update available! Click to download.",
                                                 update_url,
                                                 custom_style=("QPushButton { background-color: #333333; "
                                                               "border-radius: 12px; border: 2px solid #D5006D; } "
                                                               "QPushButton:hover { background-color: #444444; }"))
            icon_layout.addWidget(update_btn)

        # Assemble top layout.
        top_layout.addWidget(name_app)
        top_layout.addStretch()
        top_layout.addLayout(icon_layout)
        return top_layout

    def create_icon_button(self, relative_path, tooltip, url, custom_style=None):
        """
        Create a flat icon button that opens the provided URL when clicked.
        """
        btn = QPushButton()
        btn.setIcon(QIcon(Utility.resource_path(relative_path)))
        btn.setIconSize(QSize(24, 24))
        btn.setFlat(True)
        btn.setToolTip(tooltip)
        if custom_style:
            btn.setStyleSheet(custom_style)
        btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
        return btn

    def init_config_watcher(self):
        """
        Initializes a file watcher to monitor changes in the configuration file.
        Automatically updates the bot's configuration when the file changes.
        """
        try:
            event_handler = ConfigFileChangeHandler(self.bot)
            self.observer = Observer()
            self.observer.schedule(event_handler, path=ConfigManager.CONFIG_DIRECTORY, recursive=False)
            self.observer.start()
            logger.info("Config file watcher started successfully.")
        except Exception as e:
            logger.error("Failed to initialize config watcher: %s", e)

    def closeEvent(self, event):
        """
        Handles application close event to ensure resources are cleaned up:
        - Stops the file watcher.
        - Stops the bot if it is running.
        """
        try:
            if hasattr(self, 'observer'):
                self.observer.stop()
                self.observer.join()
        except Exception as e:
            logger.error("Error stopping observer: %s", e)

        if self.bot.is_running:
            self.bot.stop()
            if hasattr(self, 'bot_thread') and self.bot_thread is not None:
                self.bot_thread.join(timeout=2)
                if self.bot_thread.is_alive():
                    logger.warning("Bot thread did not terminate cleanly.")
                self.bot_thread = None
        event.accept()

    def start_bot(self):
        """
        Starts the bot if it is not already running:
        - Ensures the game process (cs2.exe) is running.
        - Launches the bot in a separate thread.
        """
        if self.bot.is_running:
            QMessageBox.warning(self, "Bot Already Running", "The bot is already running.")
            return

        if not Utility.is_game_running():
            QMessageBox.critical(self, "Game Not Running", "Could not find cs2.exe process. Make sure the game is running.")
            return

        # Clear the stop event to ensure the bot runs.
        self.bot.stop_event.clear()
        self.bot_thread = threading.Thread(target=self.bot.start, daemon=True)
        self.bot_thread.start()

        self.status_label.setText("Bot Status: Active")
        self.status_label.setStyleSheet("font-size: 16px; color: #008000; font-weight: bold;")

    def stop_bot(self):
        """
        Stops the bot if it is currently running:
        - Signals the bot's stop event to terminate its main loop.
        - Waits for the bot's thread to terminate and updates the UI.
        """
        if not self.bot.is_running:
            QMessageBox.warning(self, "Bot Not Started", "The bot is not running.")
            return

        self.bot.stop()
        if hasattr(self, 'bot_thread') and self.bot_thread is not None:
            self.bot_thread.join(timeout=2)
            if self.bot_thread.is_alive():
                logger.warning("Bot thread did not terminate cleanly.")
            self.bot_thread = None

        self.status_label.setText("Bot Status: Inactive")
        self.status_label.setStyleSheet("font-size: 16px; color: #FF0000; font-weight: bold;")

    def save_general_settings(self):
        """
        Saves the user's changes to the bot's configuration:
        - Validates user inputs.
        - Updates the bot's configuration with new values.
        - Persists the updated configuration using the ConfigManager.
        """
        try:
            self.validate_inputs()
            settings = self.bot.config['Settings']
            settings['TriggerKey'] = self.trigger_key_input.text().strip()
            settings['ToggleMode'] = self.toggle_mode_checkbox.isChecked()
            settings['AttackOnTeammates'] = self.attack_teammates_checkbox.isChecked()
            settings['ShotDelayMin'] = float(self.min_delay_input.text())
            settings['ShotDelayMax'] = float(self.max_delay_input.text())
            settings['PostShotDelay'] = float(self.post_shot_delay_input.text())
            ConfigManager.save_config(self.bot.config)
            self.bot.update_config(self.bot.config)
            QMessageBox.information(self, "Settings Saved", "Configuration has been successfully saved.")
        except ValueError as e:
            QMessageBox.critical(self, "Invalid Input", str(e))

    def validate_inputs(self):
        """
        Validates user input fields in the General Settings tab.
        Ensures all required fields have valid values.
        """
        trigger_key = self.trigger_key_input.text().strip()
        if not trigger_key:
            raise ValueError("Trigger key cannot be empty.")

        try:
            min_delay = float(self.min_delay_input.text().strip())
            max_delay = float(self.max_delay_input.text().strip())
            post_delay = float(self.post_shot_delay_input.text().strip())
        except ValueError:
            raise ValueError("Delay values must be valid numbers.")

        if min_delay < 0 or max_delay < 0 or post_delay < 0:
            raise ValueError("Delay values must be non-negative.")
        if min_delay > max_delay:
            raise ValueError("Minimum delay cannot be greater than maximum delay.")

    def update_log_output(self):
        """
        Periodically updates the Logs tab with new log entries from the log file.
        Appends new log entries since the last read position to the log display.
        """
        try:
            # Check the current size of the log file.
            file_size = os.path.getsize(Logger.LOG_FILE)
            
            # If the file has been truncated or rotated, reset the position.
            if file_size < self.last_log_position:
                self.last_log_position = 0
            
            # If there's no new content, exit early.
            if self.last_log_position == file_size:
                return
            
            with open(Logger.LOG_FILE, 'r') as log_file:
                log_file.seek(self.last_log_position)
                new_logs = log_file.read()
                # Update the last read position.
                self.last_log_position = log_file.tell()
                
                if new_logs:
                    self.log_output.insertPlainText(new_logs)
                    self.log_output.ensureCursorVisible()
        except Exception as e:
            self.log_output.append(f"Failed to read log file: {e}")
            self.log_output.ensureCursorVisible()