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
from classes.config_manager import ConfigManager
from classes.file_watcher import ConfigFileChangeHandler
from classes.logger import Logger

from gui.home_tab import populate_dashboard
from gui.general_settings_tab import populate_settings
from gui.logs_tab import populate_logs
from gui.faq_tab import populate_faq
from gui.supporters_tab import populate_supporters

# Cache the logger instance for consistent logging throughout the application
logger = Logger.get_logger()

class MainWindow:
    def __init__(self):
        """Initialize the main application window and setup UI components."""
        # Define repository URL for reference
        self.repo_url = "github.com/Jesewe/cs2-triggerbot"
        # Initialize bot thread, observer, and log timer as None until set up
        self.bot_thread = None
        self.observer = None
        self.log_timer = None
        # Track the last position in the log file for incremental updates
        self.last_log_position = 0
        
        # Configure CustomTkinter with a modern dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Fetch offsets and client data, initialize the TriggerBot instance
        offsets, client_data = self.fetch_offsets_or_warn()
        self.bot = CS2TriggerBot(offsets, client_data)
        
        # Create the main window with a title and initial size
        self.root = ctk.CTk()
        self.root.title(f"CS2 TriggerBot {ConfigManager.VERSION}")
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
        
        # Main title "CS2" with accent color
        main_title = ctk.CTkLabel(
            title_frame,
            text="CS2",
            font=("Chivo", 28, "bold"),
            text_color="#D5006D"
        )
        main_title.pack(side="left")
        
        # Subtitle "TriggerBot" in white
        sub_title = ctk.CTkLabel(
            title_frame,
            text="TriggerBot",
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
        
        # Status dot indicating bot activity
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
            command=lambda: webbrowser.open("https://github.com/Jesewe/cs2-triggerbot"),
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
            command=lambda: webbrowser.open("https://boosty.to/jesewe"),
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
            temp_exe = os.path.join(ConfigManager.UPDATE_DIRECTORY, "new_CS2.Triggerbot.exe")
            bat_file = os.path.join(ConfigManager.UPDATE_DIRECTORY, "update.bat")
            
            # Download the new executable
            with open(temp_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info("Update downloaded successfully")
            
            # Create a batch file to handle the update process
            with open(bat_file, 'w') as f:
                f.write(f'''@echo off
title CS2 TriggerBot Updater
echo Updating CS2 TriggerBot...
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
        self.settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.logs_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.faq_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.supporters_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Populate tab frames once during initialization
        self.populate_dashboard()
        self.populate_settings()
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
            ("Settings", "settings", "⚙️"),
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
        self.settings_frame.pack_forget()
        self.logs_frame.pack_forget()
        self.faq_frame.pack_forget()
        self.supporters_frame.pack_forget()
        
        # Show the selected frame and update if necessary
        if view_key == "dashboard":
            self.dashboard_frame.pack(fill="both", expand=True)
        elif view_key == "settings":
            self.update_settings_fields()
            self.settings_frame.pack(fill="both", expand=True)
        elif view_key == "logs":
            self.logs_frame.pack(fill="both", expand=True)
        elif view_key == "faq":
            self.faq_frame.pack(fill="both", expand=True)
        elif view_key == "supporters":
            self.supporters_frame.pack(fill="both", expand=True)

    def populate_dashboard(self):
        """Populate the dashboard frame with controls and stats."""
        populate_dashboard(self, self.dashboard_frame)

    def populate_settings(self):
        """Populate the settings frame with configuration options."""
        populate_settings(self, self.settings_frame)

    def populate_logs(self):
        """Populate the logs frame with log display."""
        populate_logs(self, self.logs_frame)

    def populate_faq(self):
        """Populate the FAQ frame with questions and answers."""
        populate_faq(self, self.faq_frame)

    def populate_supporters(self):
        """Populate the supporters frame with supporter data."""
        populate_supporters(self, self.supporters_frame)

    def update_settings_fields(self):
        """Update the settings input fields with current configuration."""
        # Retrieve current settings
        settings = self.bot.config.get('Settings', {})
        # Update trigger key field
        self.trigger_key_entry.delete(0, 'end')
        self.trigger_key_entry.insert(0, settings.get('TriggerKey', ''))
        # Update toggle mode checkbox
        self.toggle_mode_var.set(settings.get('ToggleMode', False))
        # Update attack teammates checkbox
        self.attack_teammates_var.set(settings.get('AttackOnTeammates', False))
        # Update minimum delay field
        self.min_delay_entry.delete(0, 'end')
        self.min_delay_entry.insert(0, str(settings.get('ShotDelayMin', 0.01)))
        # Update maximum delay field
        self.max_delay_entry.delete(0, 'end')
        self.max_delay_entry.insert(0, str(settings.get('ShotDelayMax', 0.03)))
        # Update post-shot delay field
        self.post_shot_delay_entry.delete(0, 'end')
        self.post_shot_delay_entry.insert(0, str(settings.get('PostShotDelay', 0.1)))

    def fetch_offsets_or_warn(self):
        """Attempt to fetch offsets; warn the user and return empty dictionaries on failure."""
        try:
            offsets, client_data = Utility.fetch_offsets()
            if offsets is None or client_data is None:
                raise ValueError("Failed to fetch offsets from the server.")
            return offsets, client_data
        except Exception as e:
            logger.error("Offsets fetch error: %s", e)
            return {}, {}

    def update_bot_status(self, status, color):
        """Update bot status in header and dashboard."""
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

    def start_bot(self):
        """Start the bot if it is not already running."""
        # Check if bot is already active
        if self.bot.is_running:
            messagebox.showwarning("Bot Already Running", "The bot is already running.")
            return

        # Verify if the game is running
        if not Utility.is_game_running():
            messagebox.showerror("Game Not Running", "Could not find cs2.exe process. Make sure the game is running.")
            return

        # Clear stop event and start bot in a new thread
        self.bot.stop_event.clear()
        self.bot_thread = threading.Thread(target=self.bot.start, daemon=True)
        self.bot_thread.start()

        # Update UI to reflect active status
        self.update_bot_status("Active", "#22c55e")

    def stop_bot(self):
        """Stop the bot if it is currently running."""
        # Check if bot is not running
        if not self.bot.is_running:
            messagebox.showwarning("Bot Not Started", "The bot is not running.")
            return

        # Stop the bot and wait for the thread to finish
        self.bot.stop()
        if hasattr(self, 'bot_thread') and self.bot_thread is not None:
            self.bot_thread.join(timeout=2)
            if self.bot_thread.is_alive():
                logger.warning("Bot thread did not terminate cleanly.")
            self.bot_thread = None

        # Update UI to reflect inactive status
        self.update_bot_status("Inactive", "#ef4444")

    def save_settings(self, show_message=True):
        """Save the configuration settings."""
        try:
            # Validate input fields
            self.validate_inputs()
            
            # Update configuration with current values
            settings = self.bot.config['Settings']
            settings['TriggerKey'] = self.trigger_key_entry.get().strip()
            settings['ToggleMode'] = self.toggle_mode_var.get()
            settings['AttackOnTeammates'] = self.attack_teammates_var.get()
            settings['ShotDelayMin'] = float(self.min_delay_entry.get())
            settings['ShotDelayMax'] = float(self.max_delay_entry.get())
            settings['PostShotDelay'] = float(self.post_shot_delay_entry.get())
            
            # Save and apply the updated configuration
            ConfigManager.save_config(self.bot.config)
            self.bot.update_config(self.bot.config)
            if show_message:
                messagebox.showinfo("Settings Saved", "Configuration has been successfully saved.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def validate_inputs(self):
        """Validate user input fields."""
        # Check if trigger key is provided
        trigger_key = self.trigger_key_entry.get().strip()
        if not trigger_key:
            raise ValueError("Trigger key cannot be empty.")

        # Validate delay fields as numbers
        try:
            min_delay = float(self.min_delay_entry.get())
            max_delay = float(self.max_delay_entry.get())
            post_delay = float(self.post_shot_delay_entry.get())
        except ValueError:
            raise ValueError("Delay values must be valid numbers.")

        # Ensure delays are non-negative and logical
        if min_delay < 0 or max_delay < 0 or post_delay < 0:
            raise ValueError("Delay values must be non-negative.")
        if min_delay > max_delay:
            raise ValueError("Minimum delay cannot be greater than maximum delay.")

    def reset_to_defaults(self):
        """Reset all settings to default values."""
        # Retrieve default settings
        defaults = ConfigManager.DEFAULT_CONFIG['Settings']
        
        # Reset trigger key
        self.trigger_key_entry.delete(0, 'end')
        self.trigger_key_entry.insert(0, defaults.get('TriggerKey', ''))
        
        # Reset toggle mode and attack teammates
        self.toggle_mode_var.set(defaults.get('ToggleMode', False))
        self.attack_teammates_var.set(defaults.get('AttackOnTeammates', False))
        
        # Reset delay fields
        self.min_delay_entry.delete(0, 'end')
        self.min_delay_entry.insert(0, str(defaults.get('ShotDelayMin', 0.01)))
        self.max_delay_entry.delete(0, 'end')
        self.max_delay_entry.insert(0, str(defaults.get('ShotDelayMax', 0.03)))
        self.post_shot_delay_entry.delete(0, 'end')
        self.post_shot_delay_entry.insert(0, str(defaults.get('PostShotDelay', 0.1)))
        
        # Save without showing a message
        self.save_settings(show_message=False)
        messagebox.showinfo("Settings Reset", "All settings have been reset to default values.")

    def open_config_directory(self):
        """Open the configuration directory in the file explorer."""
        path = ConfigManager.CONFIG_DIRECTORY
        if platform.system() == "Windows":
            os.startfile(path)

    def show_share_import_dialog(self):
        """Show modern share/import dialog for configuration sharing."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Share/Import Settings")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Center the dialog relative to the main window
        self.root.update_idletasks()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        dialog_w = 600
        dialog_h = 500
        x = root_x + (root_w // 2) - (dialog_w // 2)
        y = root_y + (root_h // 2) - (dialog_h // 2)
        dialog.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")
        
        # Main frame for dialog content
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Dialog title
        ctk.CTkLabel(
            main_frame,
            text="🔗 Share/Import Configuration",
            font=("Chivo", 24, "bold"),
            text_color=("#1f2937", "#E0E0E0")
        ).pack(pady=(0, 20))
        
        # Description of dialog purpose
        ctk.CTkLabel(
            main_frame,
            text="Generate a shareable code for your settings or import settings from a code",
            font=("Gambetta", 14),
            text_color=("#6b7280", "#9ca3af")
        ).pack(pady=(0, 30))
        
        # Text area for displaying or entering codes
        text_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=12,
            fg_color=("#f8fafc", "#0d1117"),
            border_width=1,
            border_color=("#e5e7eb", "#30363d")
        )
        text_frame.pack(fill="both", expand=True, pady=(0, 30))
        
        self.share_import_text = ctk.CTkTextbox(
            text_frame,
            corner_radius=12,
            border_width=0,
            state="disabled",
            font=("Chivo", 12),
            fg_color="transparent"
        )
        self.share_import_text.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Buttons frame for actions
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        # Generate code button
        ctk.CTkButton(
            buttons_frame,
            text="📤 Generate Code",
            command=self.export_settings,
            width=140,
            height=40,
            corner_radius=10,
            fg_color="#22c55e",
            hover_color="#16a34a",
            font=("Chivo", 14, "bold")
        ).pack(side="left", padx=(0, 10))
        
        # Import settings button
        ctk.CTkButton(
            buttons_frame,
            text="📥 Import Settings",
            command=lambda: self.import_settings(dialog),
            width=140,
            height=40,
            corner_radius=10,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=("Chivo", 14, "bold")
        ).pack(side="left", padx=(0, 10))
        
        # Close dialog button
        ctk.CTkButton(
            buttons_frame,
            text="❌ Close",
            command=dialog.destroy,
            width=100,
            height=40,
            corner_radius=10,
            fg_color="#6b7280",
            hover_color="#4b5563",
            font=("Chivo", 14, "bold")
        ).pack(side="right")

    def export_settings(self):
        """Export settings to a shareable code."""
        # Collect current settings into a dictionary
        settings = {
            'TriggerKey': self.trigger_key_entry.get(),
            'ToggleMode': self.toggle_mode_var.get(),
            'ShotDelayMin': float(self.min_delay_entry.get()),
            'ShotDelayMax': float(self.max_delay_entry.get()),
            'PostShotDelay': float(self.post_shot_delay_entry.get()),
            'AttackOnTeammates': self.attack_teammates_var.get()
        }
        
        # Serialize, compress, and encode the settings
        json_bytes = orjson.dumps(settings)
        compressed = zlib.compress(json_bytes)
        encoded = base64.b64encode(compressed).decode()
        code = f"TB-{encoded}"
        
        # Display and copy the code to clipboard
        self.share_import_text.configure(state="normal")
        self.share_import_text.delete("1.0", "end")
        self.share_import_text.insert("1.0", code)
        self.share_import_text.configure(state="disabled")
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        
        messagebox.showinfo("Code Generated", "Settings code has been generated and copied to clipboard!")

    def import_settings(self, dialog):
        """Import settings from a provided code."""
        # Enable text box to read the code
        self.share_import_text.configure(state="normal")
        code = self.share_import_text.get("1.0", "end-1c").strip()
        self.share_import_text.configure(state="disabled")
        
        # Validate code prefix
        if not code.startswith("TB-"):
            messagebox.showerror("Invalid Code", "Invalid code format. Must start with 'TB-'")
            return
        
        try:
            # Decode, decompress, and deserialize the settings
            encoded = code[3:]
            compressed = base64.b64decode(encoded)
            json_bytes = zlib.decompress(compressed)
            settings = orjson.loads(json_bytes)
            
            # Update UI fields with imported settings
            self.trigger_key_entry.delete(0, 'end')
            self.trigger_key_entry.insert(0, settings.get('TriggerKey', ''))
            self.toggle_mode_var.set(settings.get('ToggleMode', False))
            self.attack_teammates_var.set(settings.get('AttackOnTeammates', False))
            self.min_delay_entry.delete(0, 'end')
            self.min_delay_entry.insert(0, str(settings.get('ShotDelayMin', 0.01)))
            self.max_delay_entry.delete(0, 'end')
            self.max_delay_entry.insert(0, str(settings.get('ShotDelayMax', 0.03)))
            self.post_shot_delay_entry.delete(0, 'end')
            self.post_shot_delay_entry.insert(0, str(settings.get('PostShotDelay', 0.1)))
            
            # Save settings and close dialog
            self.save_settings(show_message=False)
            dialog.destroy()
            messagebox.showinfo("Import Successful", "Settings have been imported and saved successfully!")
        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing settings: {str(e)}")

    def init_config_watcher(self):
        """Initialize file watcher for configuration changes."""
        try:
            # Set up a watcher for config file changes
            event_handler = ConfigFileChangeHandler(self.bot)
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
                time.sleep(1)

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
            # Stop the file watcher if it exists
            if hasattr(self, 'observer') and self.observer:
                self.observer.stop()
                self.observer.join()
        except Exception as e:
            logger.error("Error stopping observer: %s", e)

        # Stop the bot if it’s running
        if self.bot.is_running:
            self.bot.stop()
            if hasattr(self, 'bot_thread') and self.bot_thread is not None:
                self.bot_thread.join(timeout=2)
                if self.bot_thread.is_alive():
                    logger.warning("Bot thread did not terminate cleanly.")
                self.bot_thread = None