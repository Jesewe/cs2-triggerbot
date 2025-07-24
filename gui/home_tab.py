import customtkinter as ctk
import threading
import orjson
from classes.logger import Logger
from classes.utility import Utility
from classes.config_manager import ConfigManager

# Cache the logger instance
logger = Logger.get_logger()

def populate_dashboard(main_window, frame):
    """Populate the dashboard frame with status cards, controls, and a quick start guide."""
    # Scrollable container for dashboard content
    dashboard = ctk.CTkScrollableFrame(
        frame,
        fg_color="transparent"
    )
    dashboard.pack(fill="both", expand=True, padx=40, pady=40)
    
    # Frame for page title and subtitle
    title_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
    title_frame.pack(fill="x", pady=(0, 30))
    
    # Dashboard title with icon
    title_label = ctk.CTkLabel(
        title_frame,
        text="🎯 Dashboard",
        font=("Chivo", 36, "bold"),
        text_color=("#1f2937", "#ffffff")
    )
    title_label.pack(side="left")
    
    # Subtitle providing context
    subtitle_label = ctk.CTkLabel(
        title_frame,
        text="Monitor and control your CS2 client",
        font=("Gambetta", 16),
        text_color=("#64748b", "#94a3b8")
    )
    subtitle_label.pack(side="left", padx=(20, 0), pady=(10, 0))
    
    # Frame for status cards
    stats_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
    stats_frame.pack(fill="x", pady=(0, 40))
    
    # Bot status card with stored label reference
    status_card, main_window.bot_status_label = create_stat_card(
        main_window,
        stats_frame,
        "🔮 Status",
        "Inactive",
        "#ef4444",
        "Current operational state"
    )
    status_card.pack(side="left", fill="x", expand=True, padx=(0, 20))
    
    # Last update card with stored label reference
    update_card, main_window.update_value_label = create_stat_card(
        main_window,
        stats_frame,
        "🔄 Offsets Update",
        "Checking...",
        "#6b7280",
        "Last offsets synchronization"
    )
    update_card.pack(side="left", fill="x", expand=True, padx=(10, 10))
    
    # Version card
    version_card, version_value_label = create_stat_card(
        main_window,
        stats_frame,
        "📦 Version",
        f"{ConfigManager.VERSION}",
        "#D5006D",
        "Current application version"
    )
    version_card.pack(side="left", fill="x", expand=True, padx=(20, 0))
    
    # Control panel section
    control_panel = ctk.CTkFrame(
        dashboard,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    control_panel.pack(fill="x", pady=(0, 40))
    
    # Header for control panel
    control_header = ctk.CTkFrame(control_panel, fg_color="transparent")
    control_header.pack(fill="x", padx=40, pady=(40, 30))
    
    # Control center title
    ctk.CTkLabel(
        control_header,
        text="🎮 Control Center",
        font=("Chivo", 24, "bold"),
        text_color=("#1f2937", "#ffffff")
    ).pack(side="left")
    
    # Frame for control buttons
    control_buttons = ctk.CTkFrame(control_panel, fg_color="transparent")
    control_buttons.pack(fill="x", padx=40, pady=(0, 40))
    
    # Start button with play icon
    start_button = ctk.CTkButton(
        control_buttons,
        text="▶  Start Client",
        command=main_window.start_client,
        width=180,
        height=60,
        corner_radius=20,
        fg_color=("#22c55e", "#16a34a"),
        hover_color=("#16a34a", "#15803d"),
        font=("Chivo", 18, "bold"),
        border_width=2,
        border_color=("#16a34a", "#15803d")
    )
    start_button.pack(side="left", padx=(0, 20))
    
    # Stop button with stop icon
    stop_button = ctk.CTkButton(
        control_buttons,
        text="⏹  Stop Client",
        command=main_window.stop_client,
        width=180,
        height=60,
        corner_radius=20,
        fg_color=("#ef4444", "#dc2626"),
        hover_color=("#dc2626", "#b91c1c"),
        font=("Chivo", 18, "bold"),
        border_width=2,
        border_color=("#dc2626", "#b91c1c")
    )
    stop_button.pack(side="left")
    
    # Quick start guide section
    guide_card = ctk.CTkFrame(
        dashboard,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    guide_card.pack(fill="x")
    
    # Header for quick start guide
    guide_header = ctk.CTkFrame(guide_card, fg_color="transparent")
    guide_header.pack(fill="x", padx=40, pady=(40, 30))
    
    # Guide title with icon
    ctk.CTkLabel(
        guide_header,
        text="🚀 Quick Start Guide",
        font=("Chivo", 24, "bold"),
        text_color=("#1f2937", "#ffffff")
    ).pack(side="left")
    
    # Guide subtitle
    ctk.CTkLabel(
        guide_header,
        text="Follow these steps to get started",
        font=("Gambetta", 14),
        text_color=("#64748b", "#94a3b8")
    ).pack(side="right")
    
    # List of guide steps
    steps = [
        ("1", "Launch CS2", "Open Counter-Strike 2 and ensure it's running"),
        ("2", "Configure Settings", "Set your trigger settings or overlay settings"),
        ("3", "Start Client", "Click the Start Client button to activate"),
        ("4", "Monitor Logs", "Check the Logs tab for activity and status updates")
    ]
    
    # Create each step
    for i, (step_num, step_title, step_desc) in enumerate(steps):
        # Frame for the step
        step_frame = ctk.CTkFrame(guide_card, fg_color="transparent")
        step_frame.pack(fill="x", padx=40, pady=(0, 25 if i < len(steps)-1 else 40))
        
        # Step number badge
        step_badge = ctk.CTkFrame(
            step_frame,
            width=50,
            height=50,
            corner_radius=25,
            fg_color=("#D5006D", "#E91E63")
        )
        step_badge.pack(side="left", padx=(0, 25))
        step_badge.pack_propagate(False)
        
        # Step number inside badge
        ctk.CTkLabel(
            step_badge,
            text=step_num,
            font=("Chivo", 20, "bold"),
            text_color="#ffffff"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Frame for step content
        step_content = ctk.CTkFrame(step_frame, fg_color="transparent")
        step_content.pack(side="left", fill="x", expand=True)
        
        # Step title
        ctk.CTkLabel(
            step_content,
            text=step_title,
            font=("Chivo", 18, "bold"),
            text_color=("#1f2937", "#ffffff"),
            anchor="w"
        ).pack(fill="x")
        
        # Step description
        ctk.CTkLabel(
            step_content,
            text=step_desc,
            font=("Gambetta", 14),
            text_color=("#64748b", "#94a3b8"),
            anchor="w"
        ).pack(fill="x", pady=(4, 0))
        
        # Connector line between steps (except last)
        if i < len(steps) - 1:
            connector = ctk.CTkFrame(
                guide_card,
                width=2,
                height=20,
                fg_color=("#e2e8f0", "#374151")
            )
            connector.pack(padx=(65, 0), anchor="w")
    
    # Fetch last update timestamp
    fetch_last_update(main_window)

def create_stat_card(main_window, parent, title, value, color, subtitle):
    """Create a modern stat card and return the card and value label."""
    # Card frame with modern styling
    card = ctk.CTkFrame(
        parent,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    
    # Content frame within card
    content = ctk.CTkFrame(card, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=30, pady=30)
    
    # Card header
    ctk.CTkLabel(
        content,
        text=title,
        font=("Chivo", 16, "bold"),
        text_color=("#64748b", "#94a3b8"),
        anchor="w"
    ).pack(fill="x", pady=(0, 12))
    
    # Value label with dynamic color
    value_label = ctk.CTkLabel(
        content,
        text=value,
        font=("Chivo", 28, "bold"),
        text_color=color,
        anchor="w"
    )
    value_label.pack(fill="x", pady=(0, 8))
    
    # Subtitle providing context
    ctk.CTkLabel(
        content,
        text=subtitle,
        font=("Gambetta", 13),
        text_color=("#94a3b8", "#64748b"),
        anchor="w"
    ).pack(fill="x")
    
    return card, value_label

def fetch_last_update(main_window):
    """Fetch and display the last offset update time."""
    def update_callback():
        try:
            import requests
            from dateutil.parser import parse as parse_date
            
            # Fetch latest commit data from GitHub
            response = requests.get("https://api.github.com/repos/a2x/cs2-dumper/commits/main")
            response.raise_for_status()
            commit_data = orjson.loads(response.content)
            commit_timestamp = commit_data["commit"]["committer"]["date"]
            
            # Parse and format the timestamp
            last_update_dt = parse_date(commit_timestamp)
            formatted_timestamp = last_update_dt.strftime("%m/%d/%Y %H:%M")
            
            # Update UI with formatted timestamp
            main_window.root.after(0, lambda: main_window.update_value_label.configure(
                text=formatted_timestamp, text_color="#22c55e"
            ))
        except Exception as e:
            # Display error if fetch fails
            main_window.root.after(0, lambda: main_window.update_value_label.configure(
                text="Error", text_color="#ef4444"
            ))
            logger.error("Failed to fetch last update: %s", e)
    
    # Run fetch in a separate thread
    threading.Thread(target=update_callback, daemon=True).start()

def update_client_status(self, status, color):
    """Update the client status indicators across the dashboard."""
    # Update header status label
    self.status_label.configure(text=status, text_color=color)
    # Update dashboard status label
    self.bot_status_label.configure(text=status, text_color=color)

    # Update status dot color in header
    for widget in self.status_frame.winfo_children():
        if isinstance(widget, ctk.CTkFrame) and widget.cget("width") == 12:
            widget.configure(fg_color=color)
            break
    
    # Ensure dashboard status updates if widget exists
    if hasattr(self, 'bot_status_label') and self.bot_status_label.winfo_exists():
        self.bot_status_label.configure(text=status, text_color=color)
