import os
import threading
import time
import webbrowser
import subprocess
import platform
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import orjson
import base64
import zlib
import requests
import sys

from watchdog.observers import Observer

from classes.utility import Utility
from classes.trigger_bot import CS2TriggerBot
from classes.esp import CS2Overlay
from classes.bunnyhop import CS2Bunnyhop
from classes.noflash import CS2NoFlash
from classes.config_manager import ConfigManager, COLOR_CHOICES
from classes.file_watcher import ConfigFileChangeHandler
from classes.logger import Logger

from gui.home_tab import populate_dashboard
from gui.general_settings_tab import populate_general_settings
from gui.trigger_settings_tab import populate_trigger_settings
from gui.overlay_settings_tab import populate_overlay_settings
from gui.logs_tab import populate_logs
from gui.faq_tab import populate_faq
from gui.supporters_tab import populate_supporters

# Cache the logger instance for consistent logging throughout the application
logger = Logger.get_logger()

class MainWindow:
    def __init__(self):
        """Initialize the main application window and setup UI components."""
        # Define repository URL for reference
        self.repo_url = "github.com/Jesewe/VioletWing"
        # Initialize threads, observer, and log timer as None until set up
        self.trigger_thread = None
        self.overlay_thread = None
        self.bunnyhop_thread = None
        self.noflash_thread = None
        self.observer = None
        self.log_timer = None
        # Track the last position in the log file for incremental updates
        self.last_log_position = 0
        
        # Configure CustomTkinter with a modern dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Fetch offsets and client data
        self.offsets, self.client_data, self.buttons_data = self.fetch_offsets_or_warn()

        # Initialize feature instances
        self.initialize_features()
        
        # Create the main window with a title and initial size
        self.root = ctk.CTk()
        self.root.title(f"VioletWing {ConfigManager.VERSION}")
        self.root.geometry("1300x700")
        self.root.resizable(True, True)
        self.root.minsize(1300, 700)
        
        # Set the window icon using a resource path utility
        self.root.iconbitmap(Utility.resource_path('src/img/icon.ico'))
        
        # Load custom fonts on Windows systems
        if platform.system() == "Windows":
            import ctypes
            gdi32 = ctypes.WinDLL('gdi32')
            font_files = [
                'src/fonts/Chivo-Regular.ttf',
                'src/fonts/Chivo-Bold.ttf',
                'src/fonts/Gambetta-Regular.ttf',
                'src/fonts/Gambetta-Bold.ttf'
            ]
            for font_file in font_files:
                font_path = Utility.resource_path(font_file)
                if os.path.exists(font_path):
                    gdi32.AddFontResourceW(font_path)
                else:
                    logger.warning(f"Font file not found: {font_path}")
        
        # Configure grid layout to make the UI responsive
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Initialize UI components like header and content
        self.setup_ui()
        
        # Set up configuration file watcher and log update timer
        self.init_config_watcher()
        self.start_log_timer()
        
        # Bind window close event to cleanup resources
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def initialize_features(self):
        """Initialize all feature instances with fetched offsets."""
        try:
            self.triggerbot = CS2TriggerBot(self.offsets, self.client_data, self.buttons_data)
            self.overlay = CS2Overlay(self.offsets, self.client_data, self.buttons_data)
            self.bunnyhop = CS2Bunnyhop(self.offsets, self.client_data, self.buttons_data)
            self.noflash = CS2NoFlash(self.offsets, self.client_data, self.buttons_data)
            logger.info("All features initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize features: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize features: {str(e)}")

    def setup_ui(self):
        """Setup the modern user interface components."""
        # Create a modern header with branding and controls
        self.create_modern_header()
        
        # Create the main content area including sidebar navigation
        self.create_main_content()

    def create_modern_header(self):
        """Create a sleek modern header with gradient-like appearance."""
        # Main header container with fixed height and dark background
        header_container = ctk.CTkFrame(
            self.root, 
            height=80,
            corner_radius=0,
            fg_color=("#1a1a1a", "#0d1117")
        )
        header_container.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_container.grid_propagate(False)
        header_container.grid_columnconfigure(1, weight=1)
        
        # Left side frame for logo and title
        left_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w", padx=30, pady=15)
        
        # Frame for title components
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        # Main title "Violet" with accent color
        main_title = ctk.CTkLabel(
            title_frame,
            text="Violet",
            font=("Chivo", 28, "bold"),
            text_color="#D5006D"
        )
        main_title.pack(side="left")
        
        # Subtitle "Wing" in white
        sub_title = ctk.CTkLabel(
            title_frame,
            text="Wing",
            font=("Chivo", 28, "bold"),
            text_color="#E0E0E0"
        )
        sub_title.pack(side="left", padx=(5, 0))
        
        # Version label with smaller font and gray color
        version_label = ctk.CTkLabel(
            title_frame,
            text=f"{ConfigManager.VERSION}",
            font=("Gambetta", 12),
            text_color="#6b7280"
        )
        version_label.pack(side="left", padx=(10, 0), pady=(8, 0))
        
        # Right side frame for status and action buttons
        right_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="e", padx=30, pady=15)
        
        # Status indicator frame
        self.status_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        self.status_frame.pack(side="right", padx=(20, 0))
        
        # Status dot indicating client activity
        status_dot = ctk.CTkFrame(
            self.status_frame,
            width=12,
            height=12,
            corner_radius=6,
            fg_color="#ef4444"
        )
        status_dot.pack(side="left", pady=(0, 2))
        
        # Status label showing "Inactive" or "Active"
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Inactive",
            font=("Chivo", 14, "bold"),
            text_color="#ef4444"
        )
        self.status_label.pack(side="left", padx=(8, 0))
        
        # Frame for social media buttons
        social_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        social_frame.pack(side="right")
        
        # Load social media icons using CTkImage
        try:
            github_image = Image.open(Utility.resource_path('src/img/github_icon.png'))
            self.github_ctk_image = ctk.CTkImage(light_image=github_image, dark_image=github_image, size=(24, 24))
        except FileNotFoundError:
            self.github_ctk_image = None
        
        try:
            telegram_image = Image.open(Utility.resource_path('src/img/telegram_icon.png'))
            self.telegram_ctk_image = ctk.CTkImage(light_image=telegram_image, dark_image=telegram_image, size=(24, 24))
        except FileNotFoundError:
            self.telegram_ctk_image = None

        try:
            boosty_image = Image.open(Utility.resource_path('src/img/boosty_icon.png'))
            self.boosty_ctk_image = ctk.CTkImage(light_image=boosty_image, dark_image=boosty_image, size=(24, 24))
        except FileNotFoundError:
            self.boosty_ctk_image = None
        
        # GitHub button with icon and link
        github_btn = ctk.CTkButton(
            social_frame,
            text="GitHub",
            image=self.github_ctk_image,
            compound="left",
            command=lambda: webbrowser.open("https://github.com/Jesewe/VioletWing"),
            height=32,
            corner_radius=16,
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#30363d",
            font=("Chivo", 14)
        )
        github_btn.pack(side="left", padx=(0, 8))
        
        # Telegram button with icon and link
        telegram_btn = ctk.CTkButton(
            social_frame,
            text="Telegram",
            image=self.telegram_ctk_image,
            compound="left",
            command=lambda: webbrowser.open("https://t.me/cs2_jesewe"),
            height=32,
            corner_radius=16,
            fg_color="#0088cc",
            hover_color="#006bb3",
            font=("Chivo", 14)
        )
        telegram_btn.pack(side="left", padx=(0, 8))

        # Boosty button with icon and link
        boosty_btn = ctk.CTkButton(
            social_frame,
            text="Boosty",
            image=self.boosty_ctk_image,
            compound="left",
            command=lambda: webbrowser.open("https://boosty.to/jesewe/donate"),
            height=32,
            corner_radius=16,
            fg_color="#ff6b35",
            hover_color="#e55a2b",
            font=("Chivo", 14)
        )
        boosty_btn.pack(side="left")

        # Check for updates if running as an executable
        if getattr(sys, 'frozen', False):
            logger.info("Running from executable. Checking for updates...")
            download_url = Utility.check_for_updates(ConfigManager.VERSION)
            if download_url:
                self.download_url = download_url
                # Update button shown when a new version is available
                update_btn = ctk.CTkButton(
                    social_frame,
                    text="Update Available",
                    command=self.handle_update,
                    width=80,
                    height=32,
                    corner_radius=16,
                    fg_color="#ef4444",
                    hover_color="#dc2626",
                    font=("Chivo", 14)
                )
                update_btn.pack(side="left", padx=(8, 0))
        else:
            logger.info("Running from source code. Auto-update disabled.")

    def handle_update(self):
        """Handle the update process with user confirmation."""
        # Check if download URL exists
        if not hasattr(self, 'download_url'):
            messagebox.showerror("Error", "No update available.")
            return

        # Prompt user to confirm update
        response = messagebox.askyesno("Update Available", "A new version is available. Are you ready to update?")
        if response:
            messagebox.showinfo("Updating", "Downloading update in background. You will be notified when the update is complete.")
            # Start update in a separate thread
            threading.Thread(target=self.download_and_update, args=(self.download_url,)).start()

    def download_and_update(self, download_url):
        """Download the new executable, create a .bat file to update and notify."""
        try:
            logger.info(f"Downloading update from {download_url}")
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Define paths for current and temporary executables
            current_exe = sys.executable
            exe_name = os.path.basename(current_exe)
            temp_exe = os.path.join(ConfigManager.UPDATE_DIRECTORY, "new_VioletWing.exe")
            bat_file = os.path.join(ConfigManager.UPDATE_DIRECTORY, "update.bat")
            
            # Download the new executable
            with open(temp_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info("Update downloaded successfully")
            
            # Create a batch file to handle the update process
            with open(bat_file, 'w') as f:
                f.write(f'''@echo off
title VioletWing Updater
echo Updating VioletWing...
echo.
echo Waiting for application to close...
timeout /t 3 /nobreak >nul

:WAIT_LOOP
tasklist /FI "IMAGENAME eq {exe_name}" 2>NUL | find /I /N "{exe_name}">NUL
if "%ERRORLEVEL%"=="0" (
    echo Application is still running, waiting...
    timeout /t 2 /nobreak >nul
    goto WAIT_LOOP
)

echo Backing up current version...
if exist "{current_exe}.backup" del "{current_exe}.backup"
move "{current_exe}" "{current_exe}.backup"

echo Installing new version...
move "{temp_exe}" "{current_exe}"

echo Starting updated application...
start "" "{current_exe}"

echo Update completed successfully!
timeout /t 3 /nobreak >nul

echo Cleaning up...
del "{current_exe}.backup" 2>nul
del "%~f0" 2>nul
''')
            
            logger.info(f".bat file created at {bat_file}")
            
            # Execute the batch file and close the application
            subprocess.Popen(bat_file, shell=True)
            self.root.quit()
        except Exception as e:
            logger.error(f"Failed to update: {e}")
            messagebox.showerror("Update Error", f"Failed to update: {str(e)}")

    def create_main_content(self):
        """Create the main content area with modern layout."""
        # Main container for content and sidebar
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Create sidebar navigation
        self.create_sidebar(main_container)
        
        # Content area frame
        self.content_frame = ctk.CTkFrame(
            main_container,
            corner_radius=0,
            fg_color=("#f8fafc", "#161b22")
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Frames for each tab
        self.dashboard_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.general_settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.trigger_settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.overlay_settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.logs_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.faq_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.supporters_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Populate tab frames once during initialization
        self.populate_dashboard()
        self.populate_general_settings()
        self.populate_trigger_settings()
        self.populate_overlay_settings()
        self.populate_logs()
        self.populate_faq()
        self.populate_supporters()
        
        # Show dashboard as the default view
        self.dashboard_frame.pack(fill="both", expand=True)
        self.current_view = "dashboard"

    def create_sidebar(self, parent):
        """Create modern sidebar navigation."""
        # Sidebar frame with fixed width
        sidebar = ctk.CTkFrame(
            parent,
            width=280,
            corner_radius=0,
            fg_color=("#ffffff", "#0d1117")
        )
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)
        
        # Navigation items with icons and labels
        nav_items = [
            ("Dashboard", "dashboard", "🏠"),
            ("General Settings", "general_settings", "⚙️"),
            ("Trigger Settings", "trigger_settings", "🔫"),
            ("Overlay Settings", "overlay_settings", "🌍"),
            ("Logs", "logs", "📋"),
            ("FAQ", "faq", "❓"),
            ("Supporters", "supporters", "🤝")
        ]
        
        # Dictionary to store navigation buttons
        self.nav_buttons = {}
        
        # Add padding at the top of the sidebar
        ctk.CTkFrame(sidebar, height=30, fg_color="transparent").pack(fill="x")
        
        # Create navigation buttons
        for name, key, icon in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=f"{icon}  {name}",
                command=lambda k=key: self.switch_view(k),
                width=240,
                height=50,
                corner_radius=12,
                fg_color="transparent",
                hover_color=("#e5e7eb", "#21262d"),
                text_color=("#374151", "#d1d5db"),
                font=("Chivo", 16),
                anchor="w"
            )
            btn.pack(pady=(0, 8), padx=20, fill="x")
            self.nav_buttons[key] = btn
        
        # Set the dashboard button as active by default
        self.set_active_nav("dashboard")

    def set_active_nav(self, active_key):
        """Set the active navigation button with visual feedback."""
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                # Highlight the active button
                btn.configure(
                    fg_color=("#D5006D", "#D5006D"),
                    text_color="#ffffff"
                )
            else:
                # Reset inactive buttons to default style
                btn.configure(
                    fg_color="transparent",
                    text_color=("#374151", "#d1d5db")
                )

    def switch_view(self, view_key):
        """Switch between different views by showing the appropriate frame."""
        # Avoid redundant switches
        if self.current_view == view_key:
            return
        self.current_view = view_key
        self.set_active_nav(view_key)
        
        # Hide all frames
        self.dashboard_frame.pack_forget()
        self.general_settings_frame.pack_forget()
        self.trigger_settings_frame.pack_forget()
        self.overlay_settings_frame.pack_forget()
        self.logs_frame.pack_forget()
        self.faq_frame.pack_forget()
        self.supporters_frame.pack_forget()
        
        # Show the selected frame and update if necessary
        if view_key == "dashboard":
            self.dashboard_frame.pack(fill="both", expand=True)
        elif view_key == "general_settings":
            self.general_settings_frame.pack(fill="both", expand=True)
        elif view_key == "trigger_settings":
            self.trigger_settings_frame.pack(fill="both", expand=True)
        elif view_key == "overlay_settings":
            self.overlay_settings_frame.pack(fill="both", expand=True)
        elif view_key == "logs":
            self.logs_frame.pack(fill="both", expand=True)
        elif view_key == "faq":
            self.faq_frame.pack(fill="both", expand=True)
        elif view_key == "supporters":
            self.supporters_frame.pack(fill="both", expand=True)

    def populate_dashboard(self):
        """Populate the dashboard frame with controls and stats."""
        populate_dashboard(self, self.dashboard_frame)

    def populate_general_settings(self):
        """Populate the general settings frame with configuration options."""
        populate_general_settings(self, self.general_settings_frame)

    def populate_trigger_settings(self):
        """Populate the trigger settings frame with configuration options."""
        populate_trigger_settings(self, self.trigger_settings_frame)

    def populate_overlay_settings(self):
        """Populate the overlay settings frame with configuration options."""
        populate_overlay_settings(self, self.overlay_settings_frame)

    def populate_logs(self):
        """Populate the logs frame with log display."""
        populate_logs(self, self.logs_frame)

    def populate_faq(self):
        """Populate the FAQ frame with questions and answers."""
        populate_faq(self, self.faq_frame)

    def populate_supporters(self):
        """Populate the supporters frame with supporter data."""
        populate_supporters(self, self.supporters_frame)

    def fetch_offsets_or_warn(self):
        """Attempt to fetch offsets; warn the user and return empty dictionaries on failure."""
        try:
            offsets, client_data, buttons_data = Utility.fetch_offsets()
            if offsets is None or client_data is None or buttons_data is None:
                raise ValueError("Failed to fetch offsets from the server.")
            return offsets, client_data, buttons_data
        except Exception as e:
            logger.error("Offsets fetch error: %s", e)
            messagebox.showerror("Offset Error", f"Failed to fetch offsets: {str(e)}")
            return {}, {}, {}

    def update_client_status(self, status, color):
        """Update client status in header and dashboard."""
        # Update header status label
        self.status_label.configure(text=status, text_color=color)
    
        # Update header status dot color
        for widget in self.status_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget.cget("width") == 12:
                widget.configure(fg_color=color)
                break
        
        # Update dashboard status label if it exists
        if hasattr(self, 'bot_status_label'):
            self.bot_status_label.configure(text=status, text_color=color)

    def start_client(self):
        """Start selected features based on General settings, ensuring no duplicates."""
        if not Utility.is_game_running():
            messagebox.showerror("Game Not Running", "Could not find cs2.exe process. Make sure the game is running.")
            return

        config = ConfigManager.load_config()
        any_feature_started = False

        # Start TriggerBot
        if config["General"]["Trigger"] and not getattr(self.triggerbot, 'is_running', False):
            try:
                self.triggerbot.config = config
                self.triggerbot.is_running = True
                self.trigger_thread = threading.Thread(target=self.triggerbot.start, daemon=True)
                self.trigger_thread.start()
                logger.info("TriggerBot started.")
                any_feature_started = True
            except Exception as e:
                logger.error(f"Failed to start TriggerBot: {e}")
                messagebox.showerror("TriggerBot Error", f"Failed to start TriggerBot: {str(e)}")

        # Start Overlay
        if config["General"]["Overlay"] and not getattr(self.overlay, 'is_running', False):
            try:
                self.overlay.config = config
                self.overlay.is_running = True
                self.overlay_thread = threading.Thread(target=self.overlay.start, daemon=True)
                self.overlay_thread.start()
                logger.info("Overlay started.")
                any_feature_started = True
            except Exception as e:
                logger.error(f"Failed to start Overlay: {e}")
                messagebox.showerror("Overlay Error", f"Failed to start Overlay: {str(e)}")

        # Start Bunnyhop
        if config["General"]["Bunnyhop"] and not getattr(self.bunnyhop, 'is_running', False):
            try:
                self.bunnyhop.config = config
                self.bunnyhop.is_running = True
                self.bunnyhop_thread = threading.Thread(target=self.bunnyhop.start, daemon=True)
                self.bunnyhop_thread.start()
                logger.info("Bunnyhop started.")
                any_feature_started = True
            except Exception as e:
                logger.error(f"Failed to start Bunnyhop: {e}")
                messagebox.showerror("Bunnyhop Error", f"Failed to start Bunnyhop: {str(e)}")

        # Start NoFlash
        if config["General"]["Noflash"] and not getattr(self.noflash, 'is_running', False):
            try:
                self.noflash.config = config
                self.noflash.is_running = True
                self.noflash_thread = threading.Thread(target=self.noflash.start, daemon=True)
                self.noflash_thread.start()
                logger.info("NoFlash started.")
                any_feature_started = True
            except Exception as e:
                logger.error(f"Failed to start NoFlash: {e}")
                messagebox.showerror("NoFlash Error", f"Failed to start NoFlash: {str(e)}")

        if any_feature_started:
            self.update_client_status("Active", "#22c55e")
        else:
            logger.warning("No features enabled in General settings.")
            messagebox.showwarning("No Features Enabled", "Please enable at least one feature in General Settings.")

    def stop_client(self):
        """Stop all running features and ensure threads are terminated."""
        features_stopped = False

        # Stop TriggerBot
        if self.triggerbot and getattr(self.triggerbot, 'is_running', False):
            try:
                self.triggerbot.stop()
                if self.trigger_thread and self.trigger_thread.is_alive():
                    self.trigger_thread.join(timeout=2.0)
                    if self.trigger_thread.is_alive():
                        logger.warning("TriggerBot thread did not terminate cleanly.")
                self.trigger_thread = None
                self.triggerbot.is_running = False
                logger.info("TriggerBot stopped.")
                features_stopped = True
            except Exception as e:
                logger.error(f"Failed to stop TriggerBot: {e}")

        # Stop Overlay
        if self.overlay and getattr(self.overlay, 'is_running', False):
            try:
                self.overlay.stop()
                if self.overlay_thread and self.overlay_thread.is_alive():
                    self.overlay_thread.join(timeout=2.0)
                    if self.overlay_thread.is_alive():
                        logger.warning("Overlay thread did not terminate cleanly.")
                self.overlay_thread = None
                self.overlay.is_running = False
                logger.info("Overlay stopped.")
                features_stopped = True
            except Exception as e:
                logger.error(f"Failed to stop Overlay: {e}")

        # Stop Bunnyhop
        if self.bunnyhop and getattr(self.bunnyhop, 'is_running', False):
            try:
                self.bunnyhop.stop()
                if self.bunnyhop_thread and self.bunnyhop_thread.is_alive():
                    self.bunnyhop_thread.join(timeout=2.0)
                    if self.bunnyhop_thread.is_alive():
                        logger.warning("Bunnyhop thread did not terminate cleanly.")
                self.bunnyhop_thread = None
                self.bunnyhop.is_running = False
                logger.info("Bunnyhop stopped.")
                features_stopped = True
            except Exception as e:
                logger.error(f"Failed to stop Bunnyhop: {e}")

        # Stop NoFlash
        if self.noflash and getattr(self.noflash, 'is_running', False):
            try:
                self.noflash.stop()
                if self.noflash_thread and self.noflash_thread.is_alive():
                    self.noflash_thread.join(timeout=2.0)
                    if self.noflash_thread.is_alive():
                        logger.warning("NoFlash thread did not terminate cleanly.")
                self.noflash_thread = None
                self.noflash.is_running = False
                logger.info("NoFlash stopped.")
                features_stopped = True
            except Exception as e:
                logger.error(f"Failed to stop NoFlash: {e}")

        if features_stopped:
            self.update_client_status("Inactive", "#ef4444")

    def save_settings(self, show_message=False):
        """Save the configuration settings and apply to relevant features in real-time."""
        try:
            self.validate_inputs()
            old_config = ConfigManager.load_config()
            self.update_config_from_ui()
            new_config = ConfigManager.load_config()
            ConfigManager.save_config(new_config, log_info=False)

            # Define features and their threads
            features = {
                "Trigger": (self.triggerbot, "trigger_thread"),
                "Overlay": (self.overlay, "overlay_thread"),
                "Bunnyhop": (self.bunnyhop, "bunnyhop_thread"),
                "Noflash": (self.noflash, "noflash_thread")
            }

            any_feature_running = False

            # Handle enabling/disabling and config updates
            for feature_name, (feature, thread_name) in features.items():
                old_enabled = old_config["General"].get(feature_name, False)
                new_enabled = new_config["General"].get(feature_name, False)
                is_running = getattr(feature, 'is_running', False)

                if old_enabled != new_enabled:
                    if new_enabled and not is_running:
                        # Start the feature
                        try:
                            feature.config = new_config
                            feature.is_running = True
                            thread = threading.Thread(target=feature.start, daemon=True)
                            thread.start()
                            setattr(self, thread_name, thread)
                            logger.info(f"{feature_name} started.")
                            any_feature_running = True
                        except Exception as e:
                            logger.error(f"Failed to start {feature_name}: {e}")
                    elif not new_enabled and is_running:
                        # Stop the feature
                        try:
                            feature.stop()
                            thread = getattr(self, thread_name)
                            if thread and thread.is_alive():
                                thread.join(timeout=2.0)
                                if thread.is_alive():
                                    logger.warning(f"{feature_name} thread did not terminate cleanly.")
                            setattr(self, thread_name, None)
                            feature.is_running = False
                            logger.info(f"{feature_name} stopped.")
                        except Exception as e:
                            logger.error(f"Failed to stop {feature_name}: {e}")
                if is_running:
                    # Update config for running features
                    feature.update_config(new_config)
                    logger.debug(f"Configuration updated for {feature_name}.")
                    any_feature_running = True

            # Update UI status
            if any_feature_running:
                self.update_client_status("Active", "#22c55e")
            else:
                self.update_client_status("Inactive", "#ef4444")

            if show_message:
                messagebox.showinfo("Settings Saved", "Configuration has been saved successfully.")
        except ValueError as e:
            logger.error(f"Invalid input: {e}")
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            logger.error(f"Unexpected error during save_settings: {e}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def restart_affected_features(self, old_config, new_config):
        """Restart only features affected by configuration changes."""
        any_feature_running = False

        # Helper to check if config section has changed
        def config_changed(section):
            return old_config.get(section, {}) != new_config.get(section, {})

        # Restart TriggerBot if its config changed and it's running
        if self.triggerbot.is_running and (config_changed("Trigger") or config_changed("General")):
            try:
                self.triggerbot.stop()
                if self.trigger_thread and self.trigger_thread.is_alive():
                    self.trigger_thread.join(timeout=2.0)
                self.trigger_thread = None
                if new_config["General"]["Trigger"]:
                    self.triggerbot = CS2TriggerBot(self.offsets, self.client_data, self.buttons_data)
                    self.triggerbot.config = new_config
                    self.trigger_thread = threading.Thread(target=self.triggerbot.start, daemon=True)
                    self.trigger_thread.start()
                    logger.info("TriggerBot restarted with new configuration.")
            except Exception as e:
                logger.error(f"Failed to restart TriggerBot: {e}")
            any_feature_running = True

        # Restart Overlay if its config changed and it's running
        if self.overlay.is_running and (config_changed("Overlay") or config_changed("General")):
            try:
                self.overlay.stop()
                if self.overlay_thread and self.overlay_thread.is_alive():
                    self.overlay_thread.join(timeout=2.0)
                self.overlay_thread = None
                if new_config["General"]["Overlay"]:
                    self.overlay = CS2Overlay(self.offsets, self.client_data, self.buttons_data)
                    self.overlay.config = new_config
                    self.overlay_thread = threading.Thread(target=self.overlay.start, daemon=True)
                    self.overlay_thread.start()
                    logger.info("Overlay restarted with new configuration.")
            except Exception as e:
                logger.error(f"Failed to restart Overlay: {e}")
            any_feature_running = True

        # Restart Bunnyhop if its config changed and it's running
        if self.bunnyhop.is_running and (config_changed("Bunnyhop") or config_changed("General")):
            try:
                self.bunnyhop.stop()
                if self.bunnyhop_thread and self.bunnyhop_thread.is_alive():
                    self.bunnyhop_thread.join(timeout=2.0)
                self.bunnyhop_thread = None
                if new_config["General"]["Bunnyhop"]:
                    self.bunnyhop = CS2Bunnyhop(self.offsets, self.client_data, self.buttons_data)
                    self.bunnyhop.config = new_config
                    self.bunnyhop_thread = threading.Thread(target=self.bunnyhop.start, daemon=True)
                    self.bunnyhop_thread.start()
                    logger.info("Bunnyhop restarted with new configuration.")
            except Exception as e:
                logger.error(f"Failed to restart Bunnyhop: {e}")
            any_feature_running = True

        # Restart NoFlash if its config changed and it's running
        if self.noflash.is_running and (config_changed("Noflash") or config_changed("General")):
            try:
                self.noflash.stop()
                if self.noflash_thread and self.noflash_thread.is_alive():
                    self.noflash_thread.join(timeout=2.0)
                self.noflash_thread = None
                if new_config["General"]["Noflash"]:
                    self.noflash = CS2NoFlash(self.offsets, self.client_data, self.buttons_data)
                    self.noflash.config = new_config
                    self.noflash_thread = threading.Thread(target=self.noflash.start, daemon=True)
                    self.noflash_thread.start()
                    logger.info("NoFlash restarted with new configuration.")
            except Exception as e:
                logger.error(f"Failed to restart NoFlash: {e}")
            any_feature_running = True

        # Update UI status
        if any_feature_running:
            self.update_client_status("Active", "#22c55e")
        else:
            self.update_client_status("Inactive", "#ef4444")

    def update_config_from_ui(self):
        """Update the configuration from the UI elements."""
        # Update General settings
        general_settings = self.triggerbot.config["General"]
        if hasattr(self, 'trigger_var'):
            general_settings["Trigger"] = self.trigger_var.get()
        if hasattr(self, 'overlay_var'):
            general_settings["Overlay"] = self.overlay_var.get()
        if hasattr(self, 'bunnyhop_var'):
            general_settings["Bunnyhop"] = self.bunnyhop_var.get()
        if hasattr(self, 'noflash_var'):
            general_settings["Noflash"] = self.noflash_var.get()

        # Update Trigger settings
        trigger_settings = self.triggerbot.config["Trigger"]
        if hasattr(self, 'trigger_key_entry'):
            trigger_settings["TriggerKey"] = self.trigger_key_entry.get().strip()
        if hasattr(self, 'toggle_mode_var'):
            trigger_settings["ToggleMode"] = self.toggle_mode_var.get()
        if hasattr(self, 'attack_teammates_var'):
            trigger_settings["AttackOnTeammates"] = self.attack_teammates_var.get()
        if hasattr(self, 'min_delay_entry'):
            try:
                trigger_settings["ShotDelayMin"] = float(self.min_delay_entry.get())
            except ValueError:
                pass
        if hasattr(self, 'max_delay_entry'):
            try:
                trigger_settings["ShotDelayMax"] = float(self.max_delay_entry.get())
            except ValueError:
                pass
        if hasattr(self, 'post_shot_delay_entry'):
            try:
                trigger_settings["PostShotDelay"] = float(self.post_shot_delay_entry.get())
            except ValueError:
                pass

        # Update Overlay settings
        overlay_settings = self.triggerbot.config["Overlay"]
        if hasattr(self, 'enable_box_var'):
            overlay_settings["enable_box"] = self.enable_box_var.get()
        if hasattr(self, 'box_line_thickness_slider'):
            overlay_settings["box_line_thickness"] = self.box_line_thickness_slider.get()
        if hasattr(self, 'box_color_hex_combo'):
            overlay_settings["box_color_hex"] = COLOR_CHOICES.get(self.box_color_hex_combo.get(), "#FFA500")
        if hasattr(self, 'draw_snaplines_var'):
            overlay_settings["draw_snaplines"] = self.draw_snaplines_var.get()
        if hasattr(self, 'snaplines_color_hex_combo'):
            overlay_settings["snaplines_color_hex"] = COLOR_CHOICES.get(self.snaplines_color_hex_combo.get(), "#FFFFFF")
        if hasattr(self, 'text_color_hex_combo'):
            overlay_settings["text_color_hex"] = COLOR_CHOICES.get(self.text_color_hex_combo.get(), "#FFFFFF")
        if hasattr(self, 'draw_health_numbers_var'):
            overlay_settings["draw_health_numbers"] = self.draw_health_numbers_var.get()
        if hasattr(self, 'draw_nicknames_var'):
            overlay_settings["draw_nicknames"] = self.draw_nicknames_var.get()
        if hasattr(self, 'use_transliteration_var'):
            overlay_settings["use_transliteration"] = self.use_transliteration_var.get()
        if hasattr(self, 'draw_teammates_var'):
            overlay_settings["draw_teammates"] = self.draw_teammates_var.get()
        if hasattr(self, 'teammate_color_hex_combo'):
            overlay_settings["teammate_color_hex"] = COLOR_CHOICES.get(self.teammate_color_hex_combo.get(), "#00FFFF")
        if hasattr(self, 'enable_minimap_var'):
            overlay_settings["enable_minimap"] = self.enable_minimap_var.get()
        if hasattr(self, 'minimap_size_entry'):
            try:
                minimap_size = int(self.minimap_size_entry.get())
                if 100 <= minimap_size <= 500:
                    overlay_settings["minimap_size"] = minimap_size
            except ValueError:
                pass

    def validate_inputs(self):
        """Validate user input fields."""
        # Validate Trigger settings
        if hasattr(self, 'trigger_key_entry'):
            trigger_key = self.trigger_key_entry.get().strip()
            if not trigger_key:
                raise ValueError("Trigger key cannot be empty.")

        # Validate delay fields as numbers
        if hasattr(self, 'min_delay_entry'):
            try:
                min_delay = float(self.min_delay_entry.get())
            except ValueError:
                raise ValueError("Minimum shot delay must be a valid number.")
            if min_delay < 0:
                raise ValueError("Minimum shot delay must be non-negative.")
        else:
            min_delay = None

        if hasattr(self, 'max_delay_entry'):
            try:
                max_delay = float(self.max_delay_entry.get())
            except ValueError:
                raise ValueError("Maximum shot delay must be a valid number.")
            if max_delay < 0:
                raise ValueError("Maximum shot delay must be non-negative.")
            if min_delay is not None and min_delay > max_delay:
                raise ValueError("Minimum delay cannot be greater than maximum delay.")
        else:
            max_delay = None

        if hasattr(self, 'post_shot_delay_entry'):
            try:
                post_delay = float(self.post_shot_delay_entry.get())
            except ValueError:
                raise ValueError("Post-shot delay must be a valid number.")
            if post_delay < 0:
                raise ValueError("Post-shot delay must be non-negative.")

        # Validate Overlay settings
        if hasattr(self, 'minimap_size_entry'):
            try:
                minimap_size = int(self.minimap_size_entry.get())
                if not (100 <= minimap_size <= 500):
                    raise ValueError("Minimap size must be between 100 and 500.")
            except ValueError:
                raise ValueError("Minimap size must be a valid integer.")

    def update_ui_from_config(self):
        """Update the UI elements from the configuration."""
        # Update General settings UI
        general_settings = self.triggerbot.config["General"]
        if hasattr(self, 'trigger_var'):
            self.trigger_var.set(general_settings["Trigger"])
        if hasattr(self, 'overlay_var'):
            self.overlay_var.set(general_settings["Overlay"])
        if hasattr(self, 'bunnyhop_var'):
            self.bunnyhop_var.set(general_settings["Bunnyhop"])
        if hasattr(self, 'noflash_var'):
            self.noflash_var.set(general_settings["Noflash"])

        # Update Trigger settings UI
        trigger_settings = self.triggerbot.config["Trigger"]
        if hasattr(self, 'trigger_key_entry'):
            self.trigger_key_entry.delete(0, "end")
            self.trigger_key_entry.insert(0, trigger_settings["TriggerKey"])
        if hasattr(self, 'toggle_mode_var'):
            self.toggle_mode_var.set(trigger_settings["ToggleMode"])
        if hasattr(self, 'attack_teammates_var'):
            self.attack_teammates_var.set(trigger_settings["AttackOnTeammates"])
        if hasattr(self, 'min_delay_entry'):
            self.min_delay_entry.delete(0, "end")
            self.min_delay_entry.insert(0, str(trigger_settings["ShotDelayMin"]))
        if hasattr(self, 'max_delay_entry'):
            self.max_delay_entry.delete(0, "end")
            self.max_delay_entry.insert(0, str(trigger_settings["ShotDelayMax"]))
        if hasattr(self, 'post_shot_delay_entry'):
            self.post_shot_delay_entry.delete(0, "end")
            self.post_shot_delay_entry.insert(0, str(trigger_settings["PostShotDelay"]))

        # Update Overlay settings UI
        overlay_settings = self.triggerbot.config["Overlay"]
        if hasattr(self, 'enable_box_var'):
            self.enable_box_var.set(overlay_settings["enable_box"])
        if hasattr(self, 'box_line_thickness_slider'):
            self.box_line_thickness_slider.set(overlay_settings["box_line_thickness"])
            if hasattr(self, 'box_line_thickness_value_label'):
                self.box_line_thickness_value_label.configure(text=f"{overlay_settings['box_line_thickness']:.1f}")
        if hasattr(self, 'box_color_hex_combo'):
            self.box_color_hex_combo.set(Utility.get_color_name_from_hex(overlay_settings["box_color_hex"]))
        if hasattr(self, 'draw_snaplines_var'):
            self.draw_snaplines_var.set(overlay_settings["draw_snaplines"])
        if hasattr(self, 'snaplines_color_hex_combo'):
            self.snaplines_color_hex_combo.set(Utility.get_color_name_from_hex(overlay_settings["snaplines_color_hex"]))
        if hasattr(self, 'text_color_hex_combo'):
            self.text_color_hex_combo.set(Utility.get_color_name_from_hex(overlay_settings["text_color_hex"]))
        if hasattr(self, 'draw_health_numbers_var'):
            self.draw_health_numbers_var.set(overlay_settings["draw_health_numbers"])
        if hasattr(self, 'draw_nicknames_var'):
            self.draw_nicknames_var.set(overlay_settings["draw_nicknames"])
        if hasattr(self, 'use_transliteration_var'):
            self.use_transliteration_var.set(overlay_settings["use_transliteration"])
        if hasattr(self, 'draw_teammates_var'):
            self.draw_teammates_var.set(overlay_settings["draw_teammates"])
        if hasattr(self, 'teammate_color_hex_combo'):
            self.teammate_color_hex_combo.set(Utility.get_color_name_from_hex(overlay_settings["teammate_color_hex"]))
        if hasattr(self, 'enable_minimap_var'):
            self.enable_minimap_var.set(overlay_settings["enable_minimap"])
        if hasattr(self, 'minimap_size_entry'):
            self.minimap_size_entry.delete(0, "end")
            self.minimap_size_entry.insert(0, str(overlay_settings["minimap_size"]))

    def open_config_directory(self):
        """Open the configuration directory in the file explorer."""
        path = ConfigManager.CONFIG_DIRECTORY
        if platform.system() == "Windows":
            os.startfile(path)

    def init_config_watcher(self):
        """Initialize file watcher for configuration changes."""
        try:
            # Set up a watcher for config file changes
            event_handler = ConfigFileChangeHandler(self)
            self.observer = Observer()
            self.observer.schedule(event_handler, path=ConfigManager.CONFIG_DIRECTORY, recursive=False)
            self.observer.start()
            logger.info("Config file watcher started successfully.")
        except Exception as e:
            logger.error("Failed to initialize config watcher: %s", e)

    def start_log_timer(self):
        """Start timer for updating logs in a separate thread."""
        def update_logs():
            logger = Logger.get_logger()
            while True:
                try:
                    # Update logs if the widget exists and log file is present
                    if hasattr(self, 'log_text') and os.path.exists(Logger.LOG_FILE):
                        file_size = os.path.getsize(Logger.LOG_FILE)
                        # Reset position if log file is truncated
                        if file_size < self.last_log_position:
                            self.last_log_position = 0
                        if self.last_log_position < file_size:
                            with open(Logger.LOG_FILE, 'r', encoding='utf-8') as log_file:
                                log_file.seek(self.last_log_position)
                                new_logs = log_file.read()
                                self.last_log_position = log_file.tell()
                                if new_logs:
                                    self.root.after(0, lambda logs=new_logs: self.update_log_display(logs))
                except Exception as e:
                    logger.error(f"Error in log update thread: {e}")
                time.sleep(0.1)  # Уменьшено время ожидания для большей отзывчивости

        # Start log update thread
        self.log_timer = threading.Thread(target=update_logs, daemon=True)
        self.log_timer.start()

    def update_log_display(self, new_logs):
        """Update the log display with new logs, limiting lines for performance."""
        logger = Logger.get_logger()
        try:
            # Ensure log widget exists and is valid
            if hasattr(self, 'log_text') and self.log_text.winfo_exists():
                self.log_text.configure(state="normal")
                self.log_text.insert("end", new_logs)
                self.log_text.see("end")
                
                # Limit log lines to 1000 for performance
                max_lines = 1000
                current_text = self.log_text.get("1.0", "end-1c")
                lines = current_text.splitlines()
                if len(lines) > max_lines:
                    excess_lines = len(lines) - max_lines
                    delete_to = f"{excess_lines + 1}.0"
                    self.log_text.delete("1.0", delete_to)
                
                self.log_text.configure(state="disabled")
        except Exception as e:
            logger.error(f"Error updating log display: {e}")

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()

    def on_closing(self):
        """Handle window close event by cleaning up resources."""
        self.cleanup()
        self.root.destroy()

    def cleanup(self):
        """Cleanup resources before closing the application."""
        try:
            # Stop all running features
            self.stop_client()
            
            # Stop the file watcher if it exists
            if hasattr(self, 'observer') and self.observer:
                self.observer.stop()
                self.observer.join()
        except Exception as e:
            logger.error("Error during cleanup: %s", e)