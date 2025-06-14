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
    # Main container
    main_container = ctk.CTkFrame(frame, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=24, pady=24)

    # Scrollable container
    supporters_container = ctk.CTkScrollableFrame(
        main_container, fg_color="transparent",
        scrollbar_button_color=("#CBD5E1", "#475569"),
        scrollbar_button_hover_color=("#94A3B8", "#64748B")
    )
    supporters_container.pack(fill="both", expand=True)

    # Hero section
    hero_frame = ctk.CTkFrame(
        supporters_container, corner_radius=20, fg_color=("#FFFFFF", "#0F172A"),
        border_width=2, border_color=("#E2E8F0", "#1E293B")
    )
    hero_frame.pack(fill="x", pady=(0, 48), padx=24)

    # Hero content
    hero_content = ctk.CTkFrame(hero_frame, fg_color="transparent")
    hero_content.pack(fill="x", padx=48, pady=48)

    # Title and subtitle
    ctk.CTkLabel(
        hero_content, text="🤝 Project Supporters", font=("Chivo", 48, "bold"),
        text_color=("#0F172A", "#F8FAFC")
    ).pack(anchor="w")
    ctk.CTkLabel(
        hero_content, text="Celebrating our incredible community members who fuel this project's growth",
        font=("Gambetta", 20), text_color=("#475569", "#CBD5E1"), wraplength=800
    ).pack(anchor="w", pady=(20, 0))

    # Stats frame
    stats_frame = ctk.CTkFrame(hero_content, fg_color="transparent")
    stats_frame.pack(fill="x", pady=(40, 0))

    # Content frame
    content_frame = ctk.CTkFrame(supporters_container, fg_color="transparent")
    content_frame.pack(fill="x", padx=24)

    # Loading container
    loading_container = ctk.CTkFrame(
        content_frame, corner_radius=16, fg_color=("#FFFFFF", "#1E293B"),
        border_width=1, border_color=("#E2E8F0", "#334155")
    )
    loading_container.pack(pady=24)

    # Loading content
    loading_content = ctk.CTkFrame(loading_container, fg_color="transparent")
    loading_content.pack(padx=48, pady=36)

    # Loading indicator and message
    ctk.CTkFrame(
        loading_content, width=48, height=48, corner_radius=24,
        fg_color=("#3B82F6", "#60A5FA")
    ).pack()
    ctk.CTkLabel(
        loading_content, text="Loading supporters data...", font=("Gambetta", 18),
        text_color=("#64748B", "#94A3B8")
    ).pack(pady=(20, 0))
    
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
        sections = [
            ("boosty", "early_access", "Early Access Tier", "#F59E0B", "#FEF3C7", "#92400E", "🚀 Premium members with early access to new features"),
            ("boosty", "supporter", "Community Supporters", "#3B82F6", "#DBEAFE", "#1E40AF", "💙 Valued community members supporting development")
        ]
        
        sections_created = 0
        for platform, key, title, color1, color2, color3, desc in sections:
            if platform in data and key in data[platform]:
                create_section(content_frame, title, data[platform][key], color1, color2, color3, desc)
                total_supporters += len(data[platform][key])
                sections_created += 1
        
        # Update stats display with totals
        create_stats_display(stats_frame, total_supporters, sections_created)
    
    def create_stats_display(stats_frame, total_supporters, total_tiers):
        """Create statistics display in hero section."""
        # Clear existing stats widgets
        for widget in stats_frame.winfo_children():
            widget.destroy()

        # Stats container
        container = ctk.CTkFrame(stats_frame, fg_color="transparent")
        container.pack(fill="x", pady=8)

        # Card configuration
        card_config = {'corner_radius': 16, 'width': 200, 'height': 120, 'border_width': 2}
        
        # Theme configurations
        themes = [
            {
                'fg_color': ("#E0F2FE", "#0F172A"),
                'border_color': ("#0EA5E9", "#0284C7"),
                'number_color': ("#0C4A6E", "#38BDF8"),
                'label_color': ("#0369A1", "#0EA5E9"),
                'value': total_supporters,
                'label': "Total Supporters"
            },
            {
                'fg_color': ("#F0FDF4", "#0F172A"),
                'border_color': ("#22C55E", "#16A34A"),
                'number_color': ("#15803D", "#4ADE80"),
                'label_color': ("#16A34A", "#22C55E"),
                'value': total_tiers,
                'label': "Support Tiers"
            }
        ]

        # Create stat cards
        for i, theme in enumerate(themes):
            # Card frame
            card = ctk.CTkFrame(container, fg_color=theme['fg_color'], border_color=theme['border_color'], **card_config)
            card.pack(side="left", padx=(0, 32 if i == 0 else 0))
            card.pack_propagate(False)

            # Content frame
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(expand=True, fill="both", padx=16, pady=16)

            # Value label
            ctk.CTkLabel(content, text=f"{theme['value']:,}", font=("Chivo", 36, "bold"),
                        text_color=theme['number_color']).pack(expand=True, pady=(8, 0))

            # Description label
            ctk.CTkLabel(content, text=theme['label'], font=("Gambetta", 15, "normal"),
                        text_color=theme['label_color']).pack(pady=(0, 8))
    
    def create_section(container, title, usernames, accent_color, bg_color, text_color, description):
        """Create a section for a specific supporter tier."""
        # Section wrapper
        section = ctk.CTkFrame(container, fg_color="transparent")
        section.pack(fill="x", pady=(0, 48))

        # Header frame
        header = ctk.CTkFrame(section, corner_radius=16, fg_color=("#FFFFFF", "#1E293B"), 
                            border_width=2, border_color=("#F1F5F9", "#334155"))
        header.pack(fill="x", pady=(0, 32))

        # Header content
        content = ctk.CTkFrame(header, fg_color="transparent")
        content.pack(fill="x", padx=40, pady=32)

        # Title and description
        ctk.CTkFrame(content, height=4, width=100, corner_radius=2, fg_color=accent_color).pack(anchor="w", pady=(0, 16))
        ctk.CTkLabel(content, text=title, font=("Chivo", 32, "bold"), text_color=("#0F172A", "#F8FAFC")).pack(anchor="w")
        ctk.CTkLabel(content, text=description, font=("Gambetta", 18), text_color=("#475569", "#CBD5E1")).pack(anchor="w", pady=(12, 0))

        # Member count badge
        badge = ctk.CTkFrame(content, corner_radius=24, fg_color=bg_color, height=40, border_width=1, border_color=accent_color)
        badge.pack(anchor="w", pady=(20, 0))
        ctk.CTkLabel(badge, text=f"{len(usernames)} {'member' if len(usernames) == 1 else 'members'}", 
                    font=("Chivo", 16, "bold"), text_color=text_color).pack(padx=20, pady=8)

        # Supporter usernames grid
        if usernames:
            grid = ctk.CTkFrame(section, fg_color="transparent")
            grid.pack(fill="x")
            columns = min(4, max(2, len(usernames)))

            for i, username in enumerate(usernames):
                card = ctk.CTkFrame(grid, corner_radius=12, fg_color=("#FFFFFF", "#1E293B"), 
                                border_width=1, border_color=("#E2E8F0", "#475569"), height=70)
                card.grid(row=i // columns, column=i % columns, padx=(0 if i % columns == 0 else 12, 0 if i % columns == columns - 1 else 12), 
                        pady=(0, 16), sticky="ew")
                card.grid_propagate(False)
                for c in range(columns):
                    grid.grid_columnconfigure(c, weight=1)

                card_content = ctk.CTkFrame(card, fg_color="transparent")
                card_content.pack(fill="both", expand=True, padx=24, pady=20)
                ctk.CTkFrame(card_content, width=12, height=12, corner_radius=6, fg_color=accent_color).pack(side="left")
                ctk.CTkLabel(card_content, text=username, font=("Chivo", 16, "bold"), 
                            text_color=("#1E293B", "#F1F5F9")).pack(side="left", padx=(16, 0))
    
    def show_error(loading_container, error_msg):
        """Display an error message if data fetch fails."""
        loading_container.destroy()

        # Error frame
        error_frame = ctk.CTkFrame(content_frame, corner_radius=16, fg_color=("#FEF2F2", "#1F1715"), 
                                border_width=2, border_color=("#FCA5A5", "#7F1D1D"))
        error_frame.pack(pady=24)

        # Error content
        content = ctk.CTkFrame(error_frame, fg_color="transparent")
        content.pack(padx=48, pady=36)

        # Error icon
        icon = ctk.CTkFrame(content, width=56, height=56, corner_radius=28, fg_color=("#DC2626", "#7F1D1D"))
        icon.pack()
        ctk.CTkLabel(icon, text="✕", font=("Chivo", 24, "bold"), text_color=("#FFFFFF", "#FFFFFF")).pack(expand=True)

        # Error message
        ctk.CTkLabel(content, text="Failed to Load Data", font=("Chivo", 22, "bold"), 
                    text_color=("#DC2626", "#F87171")).pack(pady=(20, 8))
        ctk.CTkLabel(content, text=error_msg, font=("Gambetta", 16), text_color=("#991B1B", "#EF4444"), 
                    wraplength=500).pack()
        ctk.CTkLabel(content, text="Please check your internet connection and try again", 
                    font=("Gambetta", 14), text_color=("#B91C1C", "#FCA5A5")).pack(pady=(12, 0))
    
    # Start fetching supporters data
    threading.Thread(target=fetch_supporters, daemon=True).start()