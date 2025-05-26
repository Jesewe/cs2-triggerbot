import customtkinter as ctk
import threading
import orjson
from classes.logger import Logger
from classes.utility import Utility

# Cache the logger instance
logger = Logger.get_logger()

def populate_dashboard(main_window, frame):
    """Populate the dashboard frame with status cards, controls, and a quick start guide."""
    # Main dashboard container with padding
    dashboard = ctk.CTkScrollableFrame(
        frame,
        fg_color="transparent"
    )
    dashboard.pack(fill="both", expand=True, padx=40, pady=40)
    
    # Page title with improved styling
    title_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
    title_frame.pack(fill="x", pady=(0, 30))
    
    # Title with accent color
    title_label = ctk.CTkLabel(
        title_frame,
        text="🎯 Dashboard",
        font=ctk.CTkFont(size=36, weight="bold"),
        text_color=("#1f2937", "#ffffff")
    )
    title_label.pack(side="left")
    
    # Subtitle
    subtitle_label = ctk.CTkLabel(
        title_frame,
        text="Monitor and control your CS2 bot",
        font=ctk.CTkFont(size=16),
        text_color=("#64748b", "#94a3b8")
    )
    subtitle_label.pack(side="left", padx=(20, 0), pady=(10, 0))
    
    # Stats cards row with improved spacing
    stats_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
    stats_frame.pack(fill="x", pady=(0, 40))
    
    # Bot status card - Store label in main_window
    status_card, main_window.bot_status_label = create_stat_card(
        main_window,
        stats_frame,
        "🤖 Bot Status",
        "Inactive",
        "#ef4444",
        "Current operational state"
    )
    status_card.pack(side="left", fill="x", expand=True, padx=(0, 20))
    
    # Last update card
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
        f"{main_window.bot.VERSION}",
        "#D5006D",
        "Current application version"
    )
    version_card.pack(side="left", fill="x", expand=True, padx=(20, 0))
    
    # Control panel with enhanced design
    control_panel = ctk.CTkFrame(
        dashboard,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    control_panel.pack(fill="x", pady=(0, 40))
    
    # Control panel header
    control_header = ctk.CTkFrame(control_panel, fg_color="transparent")
    control_header.pack(fill="x", padx=40, pady=(40, 30))
    
    # Header with icon
    ctk.CTkLabel(
        control_header,
        text="🎮 Bot Control Center",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=("#1f2937", "#ffffff")
    ).pack(side="left")
    
    # Control buttons with better icons and styling
    control_buttons = ctk.CTkFrame(control_panel, fg_color="transparent")
    control_buttons.pack(fill="x", padx=40, pady=(0, 40))
    
    # Start button with play icon
    start_button = ctk.CTkButton(
        control_buttons,
        text="▶  Start Bot",
        command=main_window.start_bot,
        width=180,
        height=60,
        corner_radius=16,
        fg_color=("#22c55e", "#16a34a"),
        hover_color=("#16a34a", "#15803d"),
        font=ctk.CTkFont(size=18, weight="bold"),
        border_width=2,
        border_color=("#16a34a", "#15803d")
    )
    start_button.pack(side="left", padx=(0, 20))
    
    # Stop button with stop icon
    stop_button = ctk.CTkButton(
        control_buttons,
        text="⏹  Stop Bot",
        command=main_window.stop_bot,
        width=180,
        height=60,
        corner_radius=16,
        fg_color=("#ef4444", "#dc2626"),
        hover_color=("#dc2626", "#b91c1c"),
        font=ctk.CTkFont(size=18, weight="bold"),
        border_width=2,
        border_color=("#dc2626", "#b91c1c")
    )
    stop_button.pack(side="left")
    
    # Quick start guide with improved design
    guide_card = ctk.CTkFrame(
        dashboard,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    guide_card.pack(fill="x")
    
    # Guide header
    guide_header = ctk.CTkFrame(guide_card, fg_color="transparent")
    guide_header.pack(fill="x", padx=40, pady=(40, 30))
    
    ctk.CTkLabel(
        guide_header,
        text="🚀 Quick Start Guide",
        font=ctk.CTkFont(size=24, weight="bold"),
        text_color=("#1f2937", "#ffffff")
    ).pack(side="left")
    
    ctk.CTkLabel(
        guide_header,
        text="Follow these steps to get started",
        font=ctk.CTkFont(size=14),
        text_color=("#64748b", "#94a3b8")
    ).pack(side="right")
    
    # Guide steps with better icons
    steps = [
        ("1", "Launch CS2", "Open Counter-Strike 2 and ensure it's running"),
        ("2", "Configure Settings", "Set your trigger key and adjust delays in Settings"),
        ("3", "Start Bot", "Click the Start Bot button to activate"),
        ("4", "Monitor Logs", "Check the Logs tab for activity and status updates")
    ]
    
    for i, (step_num, step_title, step_desc) in enumerate(steps):
        step_frame = ctk.CTkFrame(guide_card, fg_color="transparent")
        step_frame.pack(fill="x", padx=40, pady=(0, 25 if i < len(steps)-1 else 40))
        
        # Step number badge with gradient effect
        step_badge = ctk.CTkFrame(
            step_frame,
            width=50,
            height=50,
            corner_radius=25,
            fg_color=("#D5006D", "#E91E63")
        )
        step_badge.pack(side="left", padx=(0, 25))
        step_badge.pack_propagate(False)
        
        ctk.CTkLabel(
            step_badge,
            text=step_num,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#ffffff"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Step content
        step_content = ctk.CTkFrame(step_frame, fg_color="transparent")
        step_content.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            step_content,
            text=step_title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#1f2937", "#ffffff"),
            anchor="w"
        ).pack(fill="x")
        
        ctk.CTkLabel(
            step_content,
            text=step_desc,
            font=ctk.CTkFont(size=14),
            text_color=("#64748b", "#94a3b8"),
            anchor="w"
        ).pack(fill="x", pady=(4, 0))
        
        # Progress connector (except for last step)
        if i < len(steps) - 1:
            connector = ctk.CTkFrame(
                guide_card,
                width=2,
                height=20,
                fg_color=("#e2e8f0", "#374151")
            )
            connector.pack(padx=(65, 0), anchor="w")
    
    # Fetch last update
    fetch_last_update(main_window)

def create_stat_card(main_window, parent, title, value, color, subtitle):
    """Create a modern stat card and return the card and value label."""
    card = ctk.CTkFrame(
        parent,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    
    content = ctk.CTkFrame(card, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=30, pady=30)
    
    # Header
    ctk.CTkLabel(
        content,
        text=title,
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=("#64748b", "#94a3b8"),
        anchor="w"
    ).pack(fill="x", pady=(0, 12))
    
    # Value
    value_label = ctk.CTkLabel(
        content,
        text=value,
        font=ctk.CTkFont(size=28, weight="bold"),
        text_color=color,
        anchor="w"
    )
    value_label.pack(fill="x", pady=(0, 8))
    
    # Subtitle
    ctk.CTkLabel(
        content,
        text=subtitle,
        font=ctk.CTkFont(size=13),
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
            
            response = requests.get("https://api.github.com/repos/a2x/cs2-dumper/commits/main")
            response.raise_for_status()
            commit_data = orjson.loads(response.content)
            commit_timestamp = commit_data["commit"]["committer"]["date"]
            
            last_update_dt = parse_date(commit_timestamp)
            formatted_timestamp = last_update_dt.strftime("%m/%d/%Y %H:%M")
            
            # Update the stat card value directly
            main_window.root.after(0, lambda: main_window.update_value_label.configure(
                text=formatted_timestamp, text_color="#22c55e"
            ))
        except Exception as e:
            main_window.root.after(0, lambda: main_window.update_value_label.configure(
                text="Error", text_color="#ef4444"
            ))
            logger.error("Failed to fetch last update: %s", e)
    
    # Run in a separate thread to avoid blocking
    threading.Thread(target=update_callback, daemon=True).start()

def update_bot_status(main_window, is_running):
    """Update the bot status indicators across the dashboard."""
    if is_running:
        # Update status card
        main_window.bot_status_label.configure(
            text="Active", 
            text_color="#22c55e"
        )
    else:
        # Update status card  
        main_window.bot_status_label.configure(
            text="Inactive", 
            text_color="#ef4444"
        )