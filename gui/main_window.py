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

# Cache the logger instance
logger = Logger.get_logger()

class MainWindow:
    def __init__(self):
        """Initialize the main application window and setup UI components."""
        self.repo_url = "github.com/Jesewe/cs2-triggerbot"
        self.bot_thread = None
        self.observer = None
        self.log_timer = None
        self.last_log_position = 0
        
        # Configure CustomTkinter with modern dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Fetch offsets and initialize the TriggerBot
        offsets, client_data = self.fetch_offsets_or_warn()
        self.bot = CS2TriggerBot(offsets, client_data)
        
        # Create main window with better proportions
        self.root = ctk.CTk()
        self.root.title(f"CS2 TriggerBot {CS2TriggerBot.VERSION}")
        self.root.geometry("1300x700")
        self.root.resizable(True, True)
        self.root.minsize(1300, 700)
        self.root.state('zoomed')
        
        # Set window icon
        self.root.iconbitmap(Utility.resource_path('src/img/icon.ico'))
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Initialize UI components
        self.setup_ui()
        
        # Initialize file watcher and log timer
        self.init_config_watcher()
        self.start_log_timer()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """Setup the modern user interface components."""
        # Create modern header
        self.create_modern_header()
        
        # Create main content area with sidebar navigation
        self.create_main_content()

    def create_modern_header(self):
        """Create a sleek modern header with gradient like appearance."""
        # Main header container
        header_container = ctk.CTkFrame(
            self.root, 
            height=80,
            corner_radius=0,
            fg_color=("#1a1a1a", "#0d1117")
        )
        header_container.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_container.grid_propagate(False)
        header_container.grid_columnconfigure(1, weight=1)
        
        # Left side - Logo and title
        left_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="w", padx=30, pady=15)
        
        # Modern title with accent
        title_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        main_title = ctk.CTkLabel(
            title_frame,
            text="CS2",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#D5006D"  # Updated to match styles.css
        )
        main_title.pack(side="left")
        
        sub_title = ctk.CTkLabel(
            title_frame,
            text="TriggerBot",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#E0E0E0"  # Updated to match styles.css
        )
        sub_title.pack(side="left", padx=(5, 0))
        
        version_label = ctk.CTkLabel(
            title_frame,
            text=f"{CS2TriggerBot.VERSION}",
            font=ctk.CTkFont(size=12),
            text_color="#6b7280"
        )
        version_label.pack(side="left", padx=(10, 0), pady=(8, 0))
        
        # Right side - Status and actions
        right_frame = ctk.CTkFrame(header_container, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="e", padx=30, pady=15)
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        self.status_frame.pack(side="right", padx=(20, 0))
        
        status_dot = ctk.CTkFrame(
            self.status_frame,
            width=12,
            height=12,
            corner_radius=6,
            fg_color="#ef4444"
        )
        status_dot.pack(side="left", pady=(0, 2))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Inactive",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ef4444"
        )
        self.status_label.pack(side="left", padx=(8, 0))
        
        # Social buttons with modern styling
        social_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        social_frame.pack(side="right")
        
        # Load icons using CTkImage
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
            border_color="#30363d"
        )
        github_btn.pack(side="left", padx=(0, 8))
        
        telegram_btn = ctk.CTkButton(
            social_frame,
            text="Telegram",
            image=self.telegram_ctk_image,
            compound="left",
            command=lambda: webbrowser.open("https://t.me/cs2_jesewe"),
            height=32,
            corner_radius=16,
            fg_color="#0088cc",
            hover_color="#006bb3"
        )
        telegram_btn.pack(side="left")
        
        # Update button if available
        update_url = Utility.check_for_updates(CS2TriggerBot.VERSION)
        if update_url:
            update_btn = ctk.CTkButton(
                social_frame,
                text="Update!",
                command=lambda: webbrowser.open(update_url),
                width=80,
                height=32,
                corner_radius=16,
                fg_color="#ef4444",
                hover_color="#dc2626"
            )
            update_btn.pack(side="left", padx=(8, 0))

    def create_main_content(self):
        """Create the main content area with modern layout."""
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Sidebar navigation
        self.create_sidebar(main_container)
        
        # Content area
        self.content_frame = ctk.CTkFrame(
            main_container,
            corner_radius=0,
            fg_color=("#f8fafc", "#161b22")
        )
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Create frames for each tab
        self.dashboard_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.logs_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.faq_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Populate each frame once
        self.populate_dashboard()
        self.populate_settings()
        self.populate_logs()
        self.populate_faq()
        
        # Initially show the dashboard
        self.dashboard_frame.pack(fill="both", expand=True)
        self.current_view = "dashboard"

    def create_sidebar(self, parent):
        """Create modern sidebar navigation."""
        sidebar = ctk.CTkFrame(
            parent,
            width=280,
            corner_radius=0,
            fg_color=("#ffffff", "#0d1117")
        )
        sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar.grid_propagate(False)
        
        # Navigation items
        nav_items = [
            ("Dashboard", "dashboard", "🏠"),
            ("Settings", "settings", "⚙️"),
            ("Logs", "logs", "📋"),
            ("FAQ", "faq", "❓")
        ]
        
        self.nav_buttons = {}
        
        # Add some top padding
        ctk.CTkFrame(sidebar, height=30, fg_color="transparent").pack(fill="x")
        
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
                font=ctk.CTkFont(size=16),
                anchor="w"
            )
            btn.pack(pady=(0, 8), padx=20, fill="x")
            self.nav_buttons[key] = btn
        
        # Set active button
        self.set_active_nav("dashboard")

    def set_active_nav(self, active_key):
        """Set the active navigation button."""
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(
                    fg_color=("#D5006D", "#D5006D"),  # Updated to match styles.css
                    text_color="#ffffff"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("#374151", "#d1d5db")
                )

    def switch_view(self, view_key):
        """Switch between different views by showing the appropriate frame."""
        if self.current_view == view_key:
            return
        self.current_view = view_key
        self.set_active_nav(view_key)
        
        # Hide all frames
        self.dashboard_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.logs_frame.pack_forget()
        self.faq_frame.pack_forget()
        
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

    def populate_dashboard(self):
        """Populate the dashboard frame."""
        populate_dashboard(self, self.dashboard_frame)

    def populate_settings(self):
        """Populate the settings frame."""
        populate_settings(self, self.settings_frame)

    def populate_logs(self):
        """Populate the logs frame."""
        populate_logs(self, self.logs_frame)

    def populate_faq(self):
        """Populate the FAQ frame."""
        populate_faq(self, self.faq_frame)

    def update_settings_fields(self):
        """Update the settings input fields with current configuration."""
        settings = self.bot.config.get('Settings', {})
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
        self.status_label.configure(text=status, text_color=color)
        
        # Update status dot color
        for widget in self.status_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget.cget("width") == 12:
                widget.configure(fg_color=color)
                break

    def start_bot(self):
        """Start the bot if it is not already running."""
        if self.bot.is_running:
            messagebox.showwarning("Bot Already Running", "The bot is already running.")
            return

        if not Utility.is_game_running():
            messagebox.showerror("Game Not Running", "Could not find cs2.exe process. Make sure the game is running.")
            return

        # Clear the stop event to ensure the bot runs.
        self.bot.stop_event.clear()
        self.bot_thread = threading.Thread(target=self.bot.start, daemon=True)
        self.bot_thread.start()

        self.update_bot_status("Active", "#22c55e")

    def stop_bot(self):
        """Stop the bot if it is currently running."""
        if not self.bot.is_running:
            messagebox.showwarning("Bot Not Started", "The bot is not running.")
            return

        self.bot.stop()
        if hasattr(self, 'bot_thread') and self.bot_thread is not None:
            self.bot_thread.join(timeout=2)
            if self.bot_thread.is_alive():
                logger.warning("Bot thread did not terminate cleanly.")
            self.bot_thread = None

        self.update_bot_status("Inactive", "#ef4444")

    def save_settings(self):
        """Save the configuration settings."""
        try:
            self.validate_inputs()
            
            settings = self.bot.config['Settings']
            settings['TriggerKey'] = self.trigger_key_entry.get().strip()
            settings['ToggleMode'] = self.toggle_mode_var.get()
            settings['AttackOnTeammates'] = self.attack_teammates_var.get()
            settings['ShotDelayMin'] = float(self.min_delay_entry.get())
            settings['ShotDelayMax'] = float(self.max_delay_entry.get())
            settings['PostShotDelay'] = float(self.post_shot_delay_entry.get())
            
            ConfigManager.save_config(self.bot.config)
            self.bot.update_config(self.bot.config)
            messagebox.showinfo("Settings Saved", "Configuration has been successfully saved.")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def validate_inputs(self):
        """Validate user input fields."""
        trigger_key = self.trigger_key_entry.get().strip()
        if not trigger_key:
            raise ValueError("Trigger key cannot be empty.")

        try:
            min_delay = float(self.min_delay_entry.get())
            max_delay = float(self.max_delay_entry.get())
            post_delay = float(self.post_shot_delay_entry.get())
        except ValueError:
            raise ValueError("Delay values must be valid numbers.")

        if min_delay < 0 or max_delay < 0 or post_delay < 0:
            raise ValueError("Delay values must be non-negative.")
        if min_delay > max_delay:
            raise ValueError("Minimum delay cannot be greater than maximum delay.")

    def reset_to_defaults(self):
        """Reset all settings to default values."""
        defaults = ConfigManager.DEFAULT_CONFIG['Settings']
        
        self.trigger_key_entry.delete(0, 'end')
        self.trigger_key_entry.insert(0, defaults.get('TriggerKey', ''))
        
        self.toggle_mode_var.set(defaults.get('ToggleMode', False))
        self.attack_teammates_var.set(defaults.get('AttackOnTeammates', False))
        
        self.min_delay_entry.delete(0, 'end')
        self.min_delay_entry.insert(0, str(defaults.get('ShotDelayMin', 0.01)))
        
        self.max_delay_entry.delete(0, 'end')
        self.max_delay_entry.insert(0, str(defaults.get('ShotDelayMax', 0.03)))
        
        self.post_shot_delay_entry.delete(0, 'end')
        self.post_shot_delay_entry.insert(0, str(defaults.get('PostShotDelay', 0.1)))
        
        self.save_settings()

    def open_config_directory(self):
        """Open the configuration directory."""
        path = ConfigManager.CONFIG_DIRECTORY
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])

    def show_share_import_dialog(self):
        """Show modern share/import dialog."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Share/Import Settings")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 250,
            self.root.winfo_rooty() + 150
        ))
        
        # Main container
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="🔗 Share/Import Configuration",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1f2937", "#E0E0E0")  # Updated to match styles.css
        ).pack(pady=(0, 20))
        
        # Description
        ctk.CTkLabel(
            main_frame,
            text="Generate a shareable code for your settings or import settings from a code",
            font=ctk.CTkFont(size=14),
            text_color=("#6b7280", "#9ca3af")
        ).pack(pady=(0, 30))
        
        # Text area
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
            font=ctk.CTkFont(family="Consolas", size=12),
            fg_color="transparent"
        )
        self.share_import_text.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x")
        
        ctk.CTkButton(
            buttons_frame,
            text="📤 Generate Code",
            command=self.export_settings,
            width=140,
            height=40,
            corner_radius=10,
            fg_color="#22c55e",
            hover_color="#16a34a",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            buttons_frame,
            text="📥 Import Settings",
            command=lambda: self.import_settings(dialog),
            width=140,
            height=40,
            corner_radius=10,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            buttons_frame,
            text="❌ Close",
            command=dialog.destroy,
            width=100,
            height=40,
            corner_radius=10,
            fg_color="#6b7280",
            hover_color="#4b5563",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right")

    def export_settings(self):
        """Export settings to shareable code."""
        settings = {
            'TriggerKey': self.trigger_key_entry.get(),
            'ToggleMode': self.toggle_mode_var.get(),
            'ShotDelayMin': float(self.min_delay_entry.get()),
            'ShotDelayMax': float(self.max_delay_entry.get()),
            'PostShotDelay': float(self.post_shot_delay_entry.get()),
            'AttackOnTeammates': self.attack_teammates_var.get()
        }
        
        json_bytes = orjson.dumps(settings)
        compressed = zlib.compress(json_bytes)
        encoded = base64.b64encode(compressed).decode()
        code = f"TB-{encoded}"
        
        self.share_import_text.delete("1.0", "end")
        self.share_import_text.insert("1.0", code)
        self.root.clipboard_clear()
        self.root.clipboard_append(code)
        
        messagebox.showinfo("Code Generated", "Settings code has been generated and copied to clipboard!")

    def import_settings(self, dialog):
        """Import settings from code."""
        code = self.share_import_text.get("1.0", "end-1c").strip()
        if not code.startswith("TB-"):
            messagebox.showerror("Invalid Code", "Invalid code format. Must start with 'TB-'")
            return
        
        try:
            encoded = code[3:]
            compressed = base64.b64decode(encoded)
            json_bytes = zlib.decompress(compressed)
            settings = orjson.loads(json_bytes)
            
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
            
            self.save_settings()
            dialog.destroy()
            messagebox.showinfo("Import Successful", "Settings have been imported and saved successfully!")
        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing settings: {str(e)}")

    def init_config_watcher(self):
        """Initialize file watcher for configuration changes."""
        try:
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
                    if hasattr(self, 'log_text') and os.path.exists(Logger.LOG_FILE):
                        file_size = os.path.getsize(Logger.LOG_FILE)
                        # If log rotated or truncated
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

        self.log_timer = threading.Thread(target=update_logs, daemon=True)
        self.log_timer.start()

    def update_log_display(self, new_logs):
        """Update the log display with new logs."""
        logger = Logger.get_logger()
        try:
            if hasattr(self, 'log_text') and self.log_text.winfo_exists():
                self.log_text.configure(state="normal")
                self.log_text.insert("end", new_logs)
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
        except Exception as e:
            logger.error(f"Error updating log display: {e}")

    def run(self):
        """Start the application."""
        self.root.mainloop()

    def on_closing(self):
        """Handle window close event."""
        self.cleanup()
        self.root.destroy()

    def cleanup(self):
        """Cleanup resources before closing."""
        try:
            if hasattr(self, 'observer') and self.observer:
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