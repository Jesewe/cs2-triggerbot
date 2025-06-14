import customtkinter as ctk
import os
from classes.logger import Logger

def populate_logs(main_window, frame):
    """Populate the logs frame with a text widget to display logs."""
    # Clear any existing widgets in the frame to prevent duplication
    for widget in frame.winfo_children():
        widget.destroy()

    # Container for all logs UI elements
    logs_container = ctk.CTkFrame(
        frame,
        fg_color="transparent"
    )
    logs_container.pack(fill="both", expand=True, padx=20, pady=20)

    # Header section
    header_frame = ctk.CTkFrame(
        logs_container,
        fg_color="transparent",
        height=80
    )
    header_frame.pack(fill="x", pady=(0, 24))
    header_frame.pack_propagate(False)

    # Title label
    title_label = ctk.CTkLabel(
        header_frame,
        text="📋 Application Logs",
        font=ctk.CTkFont(size=28, weight="bold"),
        text_color=("#1a1a1a", "#ffffff")
    )
    title_label.pack(side="left", pady=20)

    # Subtitle label
    subtitle_label = ctk.CTkLabel(
        header_frame,
        text="Real-time application logs and system events",
        font=ctk.CTkFont(size=14),
        text_color=("#6b7280", "#9ca3af")
    )
    subtitle_label.pack(side="left", padx=(16, 0), pady=20)

    # Main logs card
    logs_card = ctk.CTkFrame(
        logs_container,
        corner_radius=12,
        fg_color=("#ffffff", "#1a1b23"),
        border_width=1,
        border_color=("#e5e7eb", "#2d3748")
    )
    logs_card.pack(fill="both", expand=True)

    # Logs header bar
    logs_header = ctk.CTkFrame(
        logs_card,
        corner_radius=0,
        height=50,
        fg_color=("#f8fafc", "#262626"),
        border_width=0
    )
    logs_header.pack(fill="x", padx=1, pady=(1, 0))
    logs_header.pack_propagate(False)

    header_content = ctk.CTkFrame(logs_header, fg_color="transparent")
    header_content.pack(fill="both", expand=True, padx=20, pady=12)

    logs_title = ctk.CTkLabel(
        header_content,
        text="System Logs",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=("#374151", "#e5e7eb")
    )
    logs_title.pack(side="left")

    # Status indicator
    status_frame = ctk.CTkFrame(header_content, fg_color="transparent")
    status_frame.pack(side="right")

    status_dot = ctk.CTkLabel(
        status_frame,
        text="●",
        font=ctk.CTkFont(size=12),
        text_color=("#10b981", "#10b981")
    )
    status_dot.pack(side="left", padx=(0, 8))

    status_text = ctk.CTkLabel(
        status_frame,
        text="Live",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=("#10b981", "#10b981")
    )
    status_text.pack(side="left")

    # Logs content area
    logs_content = ctk.CTkFrame(
        logs_card,
        corner_radius=0,
        fg_color="transparent"
    )
    logs_content.pack(fill="both", expand=True, padx=1, pady=(0, 1))

    # Text widget for logs
    main_window.log_text = ctk.CTkTextbox(
        logs_content,
        corner_radius=0,
        border_width=0,
        font=ctk.CTkFont(family="JetBrains Mono", size=11),
        fg_color=("#fafafa", "#0a0e14"),
        text_color=("#2d3748", "#cbd5e0"),
        state="disabled",
        wrap="word"
    )
    main_window.log_text.pack(fill="both", expand=True, padx=16, pady=16)

    # Initial load of existing logs
    _load_logs_safely(main_window)
    if os.path.exists(Logger.LOG_FILE):
        main_window.last_log_position = os.path.getsize(Logger.LOG_FILE)
    else:
        main_window.last_log_position = 0

def _load_logs_safely(main_window):
    """Safely load logs with duplicate prevention and proper error handling."""
    logger = Logger.get_logger()
    try:
        # If log file doesn't exist, show welcome message once
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

        # Read all log lines
        with open(Logger.LOG_FILE, 'r', encoding='utf-8') as log_file:
            raw_lines = log_file.read().splitlines()

        # Determine already displayed lines
        displayed = main_window.log_text.get("1.0", "end-1c").splitlines()
        # Filter out duplicates
        new_lines = [line for line in raw_lines if line not in displayed]

        if new_lines:
            main_window.log_text.configure(state="normal")
            if not displayed:
                # First time load: insert everything
                main_window.log_text.delete("1.0", "end")
                main_window.log_text.insert("1.0", "\n".join(new_lines) + "\n")
            else:
                # Subsequent updates: append only new entries
                main_window.log_text.insert("end", "\n".join(new_lines) + "\n")
            main_window.log_text.see("end")
            main_window.log_text.configure(state="disabled")
        elif not displayed:
            # File exists but empty
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
    main_window.log_text.configure(state="normal")
    main_window.log_text.delete("1.0", "end")
    main_window.log_text.insert("1.0", text)
    main_window.log_text.configure(state="disabled")

def _show_error_message(main_window, error_msg):
    """Display error message in the logs text area."""
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