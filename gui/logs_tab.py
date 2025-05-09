import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtCore import QTimer

from classes.logger import Logger

def init_logs_tab(main_window):
    """
    Sets up the Logs tab to display application logs.
    Attaches a read-only text area to the main window.
    """
    logs_tab = QWidget()
    layout = QVBoxLayout()
    main_window.log_output = QTextEdit()
    main_window.log_output.setReadOnly(True)

    # Initialize log tracking
    main_window.last_log_position = 0
    main_window.log_timer = QTimer(main_window)
    main_window.log_timer.timeout.connect(lambda: update_log_output(main_window))
    main_window.log_timer.start(1000)  # Update logs every second

    layout.addWidget(main_window.log_output)
    logs_tab.setLayout(layout)
    main_window.tabs.addTab(logs_tab, "Logs")

def update_log_output(main_window):
    """
    Periodically updates the Logs tab with new log entries from the log file.
    Appends new log entries since the last read position to the log display.
    """
    try:
        # Check the current size of the log file.
        file_size = os.path.getsize(Logger.LOG_FILE)

        # If the file has been truncated or rotated, reset the position.
        if file_size < main_window.last_log_position:
            main_window.last_log_position = 0

        # If there's no new content, exit early.
        if main_window.last_log_position == file_size:
            return

        with open(Logger.LOG_FILE, 'r') as log_file:
            log_file.seek(main_window.last_log_position)
            new_logs = log_file.read()
            # Update the last read position.
            main_window.last_log_position = log_file.tell()

            if new_logs:
                main_window.log_output.insertPlainText(new_logs)
                main_window.log_output.ensureCursorVisible()

    except Exception as e:
        main_window.log_output.append(f"Failed to read log file: {e}")
        main_window.log_output.ensureCursorVisible()