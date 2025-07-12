import customtkinter as ctk
import orjson
import threading
import requests
import webbrowser
from classes.logger import Logger

# Cache the logger instance
logger = Logger.get_logger()

def populate_notifications(main_window, frame):
    """Populate the Notifications tab with news from a JSON file."""
    # Clear existing widgets to prevent duplication
    for widget in frame.winfo_children():
        widget.destroy()

    # Scrollable container for notifications content
    notifications_container = ctk.CTkScrollableFrame(
        frame,
        fg_color="transparent",
        scrollbar_button_color=("#CBD5E1", "#475569"),
        scrollbar_button_hover_color=("#94A3B8", "#64748B")
    )
    notifications_container.pack(fill="both", expand=True, padx=40, pady=40)

    # Header section with fixed height
    header_frame = ctk.CTkFrame(
        notifications_container,
        fg_color="transparent",
        height=90
    )
    header_frame.pack(fill="x", pady=(0, 28))
    header_frame.pack_propagate(False)

    # Container for title and subtitle
    title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
    title_container.pack(side="left", fill="y")

    # Title label
    title_label = ctk.CTkLabel(
        title_container,
        text="🔔 Notifications",
        font=("Chivo", 32, "bold"),
        text_color=("#1f2937", "#f9fafb")
    )
    title_label.pack(anchor="w", pady=(8, 0))

    # Subtitle
    subtitle_label = ctk.CTkLabel(
        title_container,
        text="Latest news and updates for VioletWing",
        font=("Gambetta", 15),
        text_color=("#6b7280", "#9ca3af")
    )
    subtitle_label.pack(anchor="w", pady=(4, 0))

    # Loading card
    loading_card = ctk.CTkFrame(
        notifications_container,
        corner_radius=20,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=2,
        border_color=("#e2e8f0", "#2d3748")
    )
    loading_card.pack(fill="x", pady=(0, 40))

    # Loading content
    loading_content = ctk.CTkFrame(loading_card, fg_color="transparent")
    loading_content.pack(padx=48, pady=36)

    # Loading indicator and message
    ctk.CTkFrame(
        loading_content,
        width=48,
        height=48,
        corner_radius=24,
        fg_color=("#3B82F6", "#60A5FA")
    ).pack()
    ctk.CTkLabel(
        loading_content,
        text="Loading notifications data...",
        font=("Gambetta", 18),
        text_color=("#64748B", "#94A3B8")
    ).pack(pady=(20, 0))

    # Fetch notifications data in a background thread
    def fetch_notifications():
        try:
            # Fetch JSON data from GitHub with a timeout
            response = requests.get('https://raw.githubusercontent.com/Jesewe/VioletWing/refs/heads/main/src/notifications.json', timeout=10)
            response.raise_for_status()
            data = orjson.loads(response.content)
            # Validate notification data
            valid_notifications = [
                n for n in data
                if isinstance(n, dict) and "number" in n and "message" in n
            ]
            if not valid_notifications:
                main_window.root.after(0, lambda: show_error(loading_card, "No valid notifications found"))
                logger.warning("No valid notifications found in JSON data")
                return
            main_window.root.after(0, lambda: update_notifications_ui(valid_notifications, loading_card, notifications_container))
        except requests.exceptions.RequestException as e:
            main_window.root.after(0, lambda: show_error(loading_card, f"Failed to fetch notifications: {str(e)}"))
            logger.error(f"Failed to fetch notifications data: {e}")
        except orjson.JSONDecodeError as e:
            main_window.root.after(0, lambda: show_error(loading_card, "Invalid JSON data received"))
            logger.error(f"Invalid JSON data: {e}")
        except Exception as e:
            main_window.root.after(0, lambda: show_error(loading_card, f"Unexpected error: {str(e)}"))
            logger.error(f"Unexpected error: {e}")

    def update_notifications_ui(data, loading_card, container):
        """Update the UI with fetched notifications data."""
        # Remove loading card
        loading_card.destroy()

        # Sort notifications by number in descending order
        notifications = sorted(data, key=lambda x: x.get('number', 0), reverse=True)

        # Create notification cards
        for i, notification in enumerate(notifications):
            create_notification_card(container, notification, is_last=(i == len(notifications) - 1))

    def create_notification_card(container, notification, is_last=False):
        """Create a card for a single notification."""
        # Card for each notification
        notification_card = ctk.CTkFrame(
            container,
            corner_radius=20,
            fg_color=("#ffffff", "#1a1b23"),
            border_width=2,
            border_color=("#e2e8f0", "#2d3748")
        )
        notification_card.pack(fill="x", pady=(0, 40 if not is_last else 0))

        # Frame for notification header
        header_frame = ctk.CTkFrame(notification_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=24, pady=(20, 10))

        # Number badge
        number_badge = ctk.CTkFrame(
            header_frame,
            width=40,
            height=40,
            corner_radius=20,
            fg_color=("#D5006D", "#E91E63")
        )
        number_badge.pack(side="left", padx=(0, 12))
        number_badge.pack_propagate(False)

        # Number inside badge
        ctk.CTkLabel(
            number_badge,
            text=str(notification.get('number', '')),
            font=("Chivo", 16, "bold"),
            text_color="#ffffff"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Title with clickable URL if available
        title = notification.get('title', 'No Title')
        url = notification.get('url', '')
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=("Chivo", 18, "bold"),
            text_color=("#1f2937", "#ffffff") if not url else ("#D5006D", "#E91E63"),
            anchor="w",
            cursor="hand2" if url else "arrow"
        )
        title_label.pack(side="left", fill="x", expand=True)
        if url:
            title_label.bind("<Button-1>", lambda e: webbrowser.open(url))

        # Timestamp
        timestamp = notification.get('timestamp', '')
        if timestamp:
            ctk.CTkLabel(
                header_frame,
                text=timestamp,
                font=("Gambetta", 14),
                text_color=("#6b7280", "#9ca3af"),
                anchor="e"
            ).pack(side="right")

        # Frame for message text
        message_frame = ctk.CTkFrame(notification_card, fg_color="transparent")
        message_frame.pack(fill="x", padx=66, pady=(0, 20))

        # Message text with wrapping
        ctk.CTkLabel(
            message_frame,
            text=notification.get('message', 'No Message'),
            font=("Gambetta", 14),
            text_color=("#4b5563", "#9ca3af"),
            anchor="w",
            wraplength=750,
            justify="left"
        ).pack(fill="x")

    def show_error(loading_card, error_msg):
        """Display an error message if data fetch fails."""
        loading_card.destroy()

        # Error card
        error_card = ctk.CTkFrame(
            notifications_container,
            corner_radius=16,
            fg_color=("#FEF2F2", "#1F1715"),
            border_width=2,
            border_color=("#FCA5A5", "#7F1D1D")
        )
        error_card.pack(fill="x", pady=(0, 40))

        # Error content
        content = ctk.CTkFrame(error_card, fg_color="transparent")
        content.pack(padx=48, pady=36)

        # Error icon
        icon = ctk.CTkFrame(
            content,
            width=56,
            height=56,
            corner_radius=28,
            fg_color=("#DC2626", "#7F1D1D")
        )
        icon.pack()
        ctk.CTkLabel(
            icon,
            text="✕",
            font=("Chivo", 24, "bold"),
            text_color="#FFFFFF"
        ).pack(expand=True)

        # Error title
        ctk.CTkLabel(
            content,
            text="Failed to Load Notifications",
            font=("Chivo", 22, "bold"),
            text_color=("#DC2626", "#F87171")
        ).pack(pady=(20, 8))

        # Error message
        ctk.CTkLabel(
            content,
            text=error_msg,
            font=("Gambetta", 16),
            text_color=("#991B1B", "#EF4444"),
            wraplength=600
        ).pack()

        # Guidance text
        ctk.CTkLabel(
            content,
            text="Please check your internet connection or verify the notifications data.",
            font=("Gambetta", 14),
            text_color=("#B91C1C", "#FCA5A5")
        ).pack(pady=(12, 0))

    # Start fetching notifications data
    threading.Thread(target=fetch_notifications, daemon=True).start()