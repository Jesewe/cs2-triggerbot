import customtkinter as ctk
import os
from classes.logger import Logger

def populate_logs(main_window, frame):
    """Populate the logs frame with a text widget to display logs."""
    # Clear existing widgets to prevent duplication
    for widget in frame.winfo_children():
        widget.destroy()

    # Container for all logs UI elements with padding
    logs_container = ctk.CTkFrame(
        frame,
        fg_color="transparent"
    )
    logs_container.pack(fill="both", expand=True, padx=24, pady=24)

    # Header section with fixed height
    header_frame = ctk.CTkFrame(
        logs_container,
        fg_color="transparent",
        height=90
    )
    header_frame.pack(fill="x", pady=(0, 28))
    header_frame.pack_propagate(False)

    # Container for title and subtitle
    title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
    title_container.pack(side="left", fill="y")

    # Title label with bold styling
    title_label = ctk.CTkLabel(
        title_container,
        text="📋 Application Logs",
        font=("Chivo", 32, "bold"),
        text_color=("#1f2937", "#f9fafb")
    )
    title_label.pack(anchor="w", pady=(8, 0))

    # Subtitle providing context
    subtitle_label = ctk.CTkLabel(
        title_container,
        text="Real-time application logs and system events",
        font=("Gambetta", 15),
        text_color=("#6b7280", "#9ca3af")
    )
    subtitle_label.pack(anchor="w", pady=(4, 0))

    # Main card for logs display
    logs_card = ctk.CTkFrame(
        logs_container,
        corner_radius=16,
        fg_color=("#ffffff", "#18181b"),
        border_width=1,
        border_color=("#e2e8f0", "#27272a")
    )
    logs_card.pack(fill="both", expand=True)

    # Header bar within the logs card
    logs_header = ctk.CTkFrame(
        logs_card,
        height=60,
        fg_color=("#f8fafc", "#27272a"),
        border_width=0
    )
    logs_header.pack(fill="x", padx=2, pady=(2, 0))
    logs_header.pack_propagate(False)

    # Content frame for header elements
    header_content = ctk.CTkFrame(logs_header, fg_color="transparent")
    header_content.pack(fill="both", expand=True, padx=24, pady=16)

    # Logs section title
    logs_title = ctk.CTkLabel(
        header_content,
        text="System Logs",
        font=("Chivo", 18, "bold"),
        text_color=("#1f2937", "#f1f5f9")
    )
    logs_title.pack(side="left")

    # Status indicator frame
    status_frame = ctk.CTkFrame(header_content, fg_color="transparent")
    status_frame.pack(side="right")

    # Status dot indicating live updates
    status_dot = ctk.CTkLabel(
        status_frame,
        text="●",
        font=("Chivo", 14),
        text_color=("#059669", "#10b981")
    )
    status_dot.pack(side="left", padx=(0, 8))

    # Status text "Live"
    status_text = ctk.CTkLabel(
        status_frame,
        text="Live",
        font=("Chivo", 14, "bold"),
        text_color=("#059669", "#10b981")
    )
    status_text.pack(side="left")

    # Content area for log text
    logs_content = ctk.CTkFrame(
        logs_card,
        corner_radius=0,
        fg_color="transparent"
    )
    logs_content.pack(fill="both", expand=True, padx=2, pady=(0, 2))

    # Text widget to display logs
    main_window.log_text = ctk.CTkTextbox(
        logs_content,
        corner_radius=0,
        border_width=0,
        font=("Chivo", 13),
        fg_color=("#fcfcfd", "#0f0f11"),
        text_color=("#1f2937", "#e2e8f0"),
        state="disabled",
        wrap="word"
    )
    main_window.log_text.pack(fill="both", expand=True, padx=20, pady=20)

    # Load existing logs and set initial position
    _load_logs_safely(main_window)
    if os.path.exists(Logger.LOG_FILE):
        main_window.last_log_position = os.path.getsize(Logger.LOG_FILE)
    else:
        main_window.last_log_position = 0

def _load_logs_safely(main_window):
    """Safely load logs with duplicate prevention and proper error handling."""
    logger = Logger.get_logger()
    try:
        # Display welcome message if log file doesn’t exist
        if not os.path.exists(Logger.LOG_FILE):
            welcome_msg = (
                "=== Application Logs ===\n"
                "Welcome to the logs viewer!\n"
                "Logs will appear here as the application runs.\n\n"
                "[INFO] Logger initialized successfully\n"
                "[INFO] Logs tab loaded\n"
            )
            _replace_content(main_window, welcome_msg)
            return

        # Read all log lines from the file
        with open(Logger.LOG_FILE, 'r', encoding='utf-8') as log_file:
            raw_lines = log_file.read().splitlines()

        # Get currently displayed lines to avoid duplicates
        displayed = main_window.log_text.get("1.0", "end-1c").splitlines()
        # Filter out duplicates
        new_lines = [line for line in raw_lines if line not in displayed]

        if new_lines:
            main_window.log_text.configure(state="normal")
            if not displayed:
                # Initial load: replace all content
                main_window.log_text.delete("1.0", "end")
                main_window.log_text.insert("1.0", "\n".join(new_lines) + "\n")
            else:
                # Append new lines only
                main_window.log_text.insert("end", "\n".join(new_lines) + "\n")
            main_window.log_text.see("end")
            main_window.log_text.configure(state="disabled")
        elif not displayed:
            # Display message if log file is empty
            empty_msg = (
                "=== Application Logs ===\n"
                "Log file exists but is empty.\n"
                "New logs will appear here as they are generated.\n\n"
                "[INFO] Empty log file detected\n"
            )
            _replace_content(main_window, empty_msg)

    except FileNotFoundError:
        logger.warning(f"Log file {Logger.LOG_FILE} not found")
        _show_error_message(main_window, "Log file not found")
    except PermissionError:
        logger.error(f"Permission denied reading log file {Logger.LOG_FILE}")
        _show_error_message(main_window, "Permission denied accessing log file")
    except UnicodeDecodeError:
        logger.error(f"Encoding error reading log file {Logger.LOG_FILE}")
        _show_error_message(main_window, "Log file encoding error")
    except Exception as e:
        logger.error(f"Unexpected error loading logs: {e}")
        _show_error_message(main_window, f"Error loading logs: {str(e)}")

def _replace_content(main_window, text):
    """Helper to replace the entire content of the log widget."""
    # Enable widget, clear content, insert new text, and disable again
    main_window.log_text.configure(state="normal")
    main_window.log_text.delete("1.0", "end")
    main_window.log_text.insert("1.0", text)
    main_window.log_text.configure(state="disabled")

def _show_error_message(main_window, error_msg):
    """Display error message in the logs text area."""
    # Format error message with guidance
    error_display = (
        "=== Application Logs ===\n"
        "❌ Error Loading Logs\n\n"
        f"{error_msg}\n\n"
        "Please check the application logs directory and permissions.\n"
        "Try refreshing the logs tab or restarting the application.\n\n"
        f"[ERROR] {error_msg}\n"
    )
    main_window.log_text.configure(state="normal")
    main_window.log_text.delete("1.0", "end")
    main_window.log_text.insert("1.0", error_display)
    main_window.log_text.configure(state="disabled")