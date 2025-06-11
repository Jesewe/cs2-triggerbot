import customtkinter as ctk
import orjson
import threading
import requests
from classes.logger import Logger
from classes.utility import Utility

# Cache the logger instance
logger = Logger.get_logger()

def populate_supporters(main_window, frame):
    """Populate the Supporters tab with data from a JSON file."""
    # Main container for supporters content
    main_container = ctk.CTkFrame(frame, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=24, pady=24)
    
    # Scrollable container with custom scrollbar colors
    supporters_container = ctk.CTkScrollableFrame(
        main_container,
        fg_color="transparent",
        scrollbar_button_color=("#CBD5E1", "#475569"),
        scrollbar_button_hover_color=("#94A3B8", "#64748B")
    )
    supporters_container.pack(fill="both", expand=True)
    
    # Hero section with project branding
    hero_frame = ctk.CTkFrame(
        supporters_container,
        corner_radius=20,
        fg_color=("#FFFFFF", "#0F172A"),
        border_width=2,
        border_color=("#E2E8F0", "#1E293B")
    )
    hero_frame.pack(fill="x", pady=(0, 48), padx=24)
    
    # Content frame within hero section
    hero_content = ctk.CTkFrame(hero_frame, fg_color="transparent")
    hero_content.pack(fill="x", padx=48, pady=48)
    
    # Frame for title and subtitle
    title_container = ctk.CTkFrame(hero_content, fg_color="transparent")
    title_container.pack(fill="x")
    
    # Main title for supporters tab
    title_label = ctk.CTkLabel(
        title_container,
        text="🤝 Project Supporters",
        font=("Chivo", 48, "bold"),
        text_color=("#0F172A", "#F8FAFC")
    )
    title_label.pack(anchor="w")
    
    # Subtitle with wrapping
    subtitle_label = ctk.CTkLabel(
        title_container,
        text="Celebrating our incredible community members who fuel this project's growth",
        font=("Gambetta", 20),
        text_color=("#475569", "#CBD5E1"),
        wraplength=800
    )
    subtitle_label.pack(anchor="w", pady=(20, 0))
    
    # Frame for stats display
    stats_frame = ctk.CTkFrame(hero_content, fg_color="transparent")
    stats_frame.pack(fill="x", pady=(40, 0))
    
    # Content area for supporter sections
    content_frame = ctk.CTkFrame(supporters_container, fg_color="transparent")
    content_frame.pack(fill="x", padx=24)
    
    # Loading state container
    loading_container = ctk.CTkFrame(
        content_frame,
        corner_radius=16,
        fg_color=("#FFFFFF", "#1E293B"),
        border_width=1,
        border_color=("#E2E8F0", "#334155")
    )
    loading_container.pack(pady=24)
    
    # Content frame within loading container
    loading_content = ctk.CTkFrame(loading_container, fg_color="transparent")
    loading_content.pack(padx=48, pady=36)
    
    # Loading indicator circle
    loading_indicator = ctk.CTkFrame(
        loading_content,
        width=48,
        height=48,
        corner_radius=24,
        fg_color=("#3B82F6", "#60A5FA")
    )
    loading_indicator.pack()
    
    # Loading message
    loading_label = ctk.CTkLabel(
        loading_content,
        text="Loading supporters data...",
        font=("Gambetta", 18),
        text_color=("#64748B", "#94A3B8")
    )
    loading_label.pack(pady=(20, 0))
    
    # Fetch supporter data in a background thread
    def fetch_supporters():
        try:
            # Fetch JSON data from GitHub with a timeout
            response = requests.get('https://raw.githubusercontent.com/Jesewe/cs2-triggerbot/refs/heads/main/src/supporters.json', timeout=10)
            response.raise_for_status()
            data = orjson.loads(response.content)
            main_window.root.after(0, lambda: update_supporters_ui(data, loading_container, stats_frame))
        except requests.exceptions.RequestException as e:
            main_window.root.after(0, lambda: show_error(loading_container, f"Failed to fetch supporters data: {e}"))
            logger.error(f"Failed to fetch supporters data: {e}")
        except orjson.JSONDecodeError as e:
            main_window.root.after(0, lambda: show_error(loading_container, "Invalid JSON data received"))
            logger.error(f"Invalid JSON data: {e}")
        except Exception as e:
            main_window.root.after(0, lambda: show_error(loading_container, str(e)))
            logger.error(f"Unexpected error: {e}")
    
    def update_supporters_ui(data, loading_container, stats_frame):
        """Update the UI with fetched supporter data."""
        # Remove loading container
        loading_container.destroy()
        
        total_supporters = 0
        sections_created = 0
        
        # Process Boosty supporter data
        if "boosty" in data:
            boosty_data = data["boosty"]
            
            # Create Early Access section
            if "early_access" in boosty_data:
                create_section(
                    content_frame, 
                    "Early Access Tier", 
                    boosty_data["early_access"], 
                    "#F59E0B", 
                    "#FEF3C7",
                    "#92400E",
                    "🚀 Premium members with early access to new features"
                )
                total_supporters += len(boosty_data["early_access"])
                sections_created += 1
            
            # Create Community Supporters section
            if "supporter" in boosty_data:
                create_section(
                    content_frame, 
                    "Community Supporters", 
                    boosty_data["supporter"], 
                    "#3B82F6", 
                    "#DBEAFE",
                    "#1E40AF",
                    "💙 Valued community members supporting development"
                )
                total_supporters += len(boosty_data["supporter"])
                sections_created += 1
        
        # Update stats display with totals
        create_stats_display(stats_frame, total_supporters, sections_created)
    
    def create_stats_display(stats_frame, total_supporters, total_tiers):
        """Create statistics display in hero section."""
        # Clear existing stats widgets
        for widget in stats_frame.winfo_children():
            widget.destroy()
        
        # Container for stats
        stats_container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_container.pack(fill="x")
        
        # Total supporters stat card
        total_stat = ctk.CTkFrame(
            stats_container,
            corner_radius=12,
            fg_color=("#E0F2FE", "#164E63"),
            width=180,
            height=100,
            border_width=1,
            border_color=("#BAE6FD", "#0C4A6E")
        )
        total_stat.pack(side="left", padx=(0, 24))
        total_stat.pack_propagate(False)
        
        # Number of supporters
        ctk.CTkLabel(
            total_stat,
            text=str(total_supporters),
            font=("Chivo", 32, "bold"),
            text_color=("#0C4A6E", "#67E8F9")
        ).pack(pady=(20, 4))
        
        # Label for total supporters
        ctk.CTkLabel(
            total_stat,
            text="Total Supporters",
            font=("Gambetta", 14),
            text_color=("#0369A1", "#22D3EE")
        ).pack()
        
        # Support tiers stat card
        tiers_stat = ctk.CTkFrame(
            stats_container,
            corner_radius=12,
            fg_color=("#F0FDF4", "#14532D"),
            width=180,
            height=100,
            border_width=1,
            border_color=("#BBF7D0", "#166534")
        )
        tiers_stat.pack(side="left")
        tiers_stat.pack_propagate(False)
        
        # Number of tiers
        ctk.CTkLabel(
            tiers_stat,
            text=str(total_tiers),
            font=("Chivo", 32, "bold"),
            text_color=("#15803D", "#4ADE80")
        ).pack(pady=(20, 4))
        
        # Label for support tiers
        ctk.CTkLabel(
            tiers_stat,
            text="Support Tiers",
            font=("Gambetta", 14),
            text_color=("#16A34A", "#22C55E")
        ).pack()
    
    def create_section(container, title, usernames, accent_color, bg_color, text_color, description):
        """Create a section for a specific supporter tier."""
        # Wrapper frame for the section
        section_wrapper = ctk.CTkFrame(container, fg_color="transparent")
        section_wrapper.pack(fill="x", pady=(0, 48))
        
        # Header container for section title and details
        header_container = ctk.CTkFrame(
            section_wrapper,
            corner_radius=16,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=2,
            border_color=("#F1F5F9", "#334155")
        )
        header_container.pack(fill="x", pady=(0, 32))
        
        # Content frame within header
        header_content = ctk.CTkFrame(header_container, fg_color="transparent")
        header_content.pack(fill="x", padx=40, pady=32)
        
        # Frame for title and description
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(fill="x")
        
        # Accent line for visual flair
        accent_line = ctk.CTkFrame(
            title_frame,
            height=4,
            width=100,
            corner_radius=2,
            fg_color=accent_color
        )
        accent_line.pack(anchor="w", pady=(0, 16))
        
        # Section title
        ctk.CTkLabel(
            title_frame,
            text=title,
            font=("Chivo", 32, "bold"),
            text_color=("#0F172A", "#F8FAFC")
        ).pack(anchor="w")
        
        # Section description
        ctk.CTkLabel(
            title_frame,
            text=description,
            font=("Gambetta", 18),
            text_color=("#475569", "#CBD5E1")
        ).pack(anchor="w", pady=(12, 0))
        
        # Badge showing member count
        count_badge = ctk.CTkFrame(
            title_frame,
            corner_radius=24,
            fg_color=bg_color,
            height=40,
            border_width=1,
            border_color=accent_color
        )
        count_badge.pack(anchor="w", pady=(20, 0))
        
        count_text = f"{len(usernames)} {'member' if len(usernames) == 1 else 'members'}"
        ctk.CTkLabel(
            count_badge,
            text=count_text,
            font=("Chivo", 16, "bold"),
            text_color=text_color
        ).pack(padx=20, pady=8)
        
        # Grid for supporter usernames
        if usernames:
            grid_container = ctk.CTkFrame(section_wrapper, fg_color="transparent")
            grid_container.pack(fill="x")
            
            # Determine number of columns based on usernames
            columns = min(4, max(2, len(usernames)))
            
            for i, username in enumerate(usernames):
                row = i // columns
                col = i % columns
                
                # Card for each supporter
                member_card = ctk.CTkFrame(
                    grid_container,
                    corner_radius=12,
                    fg_color=("#FFFFFF", "#1E293B"),
                    border_width=1,
                    border_color=("#E2E8F0", "#475569"),
                    height=70
                )
                
                # Position card in grid
                padx_left = 0 if col == 0 else 12
                padx_right = 0 if col == columns - 1 else 12
                member_card.grid(
                    row=row, 
                    column=col, 
                    padx=(padx_left, padx_right), 
                    pady=(0, 16), 
                    sticky="ew"
                )
                member_card.grid_propagate(False)
                
                # Configure grid weights for responsiveness
                for c in range(columns):
                    grid_container.grid_columnconfigure(c, weight=1)
                
                # Content frame within card
                card_content = ctk.CTkFrame(member_card, fg_color="transparent")
                card_content.pack(fill="both", expand=True, padx=24, pady=20)
                
                # Status dot indicator
                status_dot = ctk.CTkFrame(
                    card_content,
                    width=12,
                    height=12,
                    corner_radius=6,
                    fg_color=accent_color
                )
                status_dot.pack(side="left")
                
                # Supporter username
                username_label = ctk.CTkLabel(
                    card_content,
                    text=username,
                    font=("Chivo", 16, "bold"),
                    text_color=("#1E293B", "#F1F5F9")
                )
                username_label.pack(side="left", padx=(16, 0))
    
    def show_error(loading_container, error_msg):
        """Display an error message if data fetch fails."""
        # Remove loading container
        loading_container.destroy()
        
        # Error container with red styling
        error_container = ctk.CTkFrame(
            content_frame,
            corner_radius=16,
            fg_color=("#FEF2F2", "#1F1715"),
            border_width=2,
            border_color=("#FCA5A5", "#7F1D1D")
        )
        error_container.pack(pady=24)
        
        # Content frame within error container
        error_content = ctk.CTkFrame(error_container, fg_color="transparent")
        error_content.pack(padx=48, pady=36)
        
        # Error icon circle
        error_icon = ctk.CTkFrame(
            error_content,
            width=56,
            height=56,
            corner_radius=28,
            fg_color=("#DC2626", "#7F1D1D")
        )
        error_icon.pack()
        
        # Error symbol '✕'
        ctk.CTkLabel(
            error_icon,
            text="✕",
            font=("Chivo", 24, "bold"),
            text_color=("#FFFFFF", "#FFFFFF")
        ).pack(expand=True)
        
        # Error title
        error_title = ctk.CTkLabel(
            error_content,
            text="Failed to Load Data",
            font=("Chivo", 22, "bold"),
            text_color=("#DC2626", "#F87171")
        )
        error_title.pack(pady=(20, 8))
        
        # Error details with wrapping
        error_detail = ctk.CTkLabel(
            error_content,
            text=error_msg,
            font=("Gambetta", 16),
            text_color=("#991B1B", "#EF4444"),
            wraplength=500
        )
        error_detail.pack()
        
        # Hint for retrying
        retry_hint = ctk.CTkLabel(
            error_content,
            text="Please check your internet connection and try again",
            font=("Gambetta", 14),
            text_color=("#B91C1C", "#FCA5A5")
        )
        retry_hint.pack(pady=(12, 0))
    
    # Start fetching supporters data
    threading.Thread(target=fetch_supporters, daemon=True).start()