from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

from classes.utility import Utility

def init_home_tab(main_window):
    """
    Sets up the Home tab with bot instructions, status, and control buttons.
    Attaches key widgets to the main window (e.g. status_label, start_button).
    """
    home_tab = QWidget()
    layout = QVBoxLayout()
    layout.setSpacing(15)

    # Bot status label
    main_window.status_label = QLabel("Bot Status: Inactive")
    main_window.status_label.setStyleSheet("font-size: 16px; color: #FF5252; font-weight: bold;")

    # Last offsets update label
    main_window.last_update_label = QLabel("Last offsets update: Fetching...")
    main_window.last_update_label.setStyleSheet("font-size: 14px; font-style: italic; color: #B0B0B0;")
    Utility.fetch_last_offset_update(main_window.last_update_label)

    # Quick start guide
    layout.addWidget(create_section_label("Quick Start Guide", 18))
    quick_start_text = QLabel(
        "1. Open CS2 game and ensure it’s running.<br>"
        "2. Configure trigger key and delays in <span style=\"color: #D5006D;\">General Settings</span>.<br>"
        "3. Press <span style=\"color: #D5006D;\">Start Bot</span> to activate.<br>"
        "4. Monitor bot status and logs in the '<span style=\"color: #D5006D;\">Logs</span>' tab."
    )
    quick_start_text.setStyleSheet("font-size: 14px;")
    quick_start_text.setTextFormat(Qt.TextFormat.RichText)
    quick_start_text.setWordWrap(True)
    layout.addWidget(quick_start_text)

    # Additional Information
    layout.addWidget(create_section_label("Additional Information", 18))
    additional_info_text = QLabel(
        "For more details, visit our "
        "<a href=\"https://github.com/Jesewe/cs2-triggerbot\" style=\"color: #D5006D; text-decoration: underline;\">GitHub repository</a> "
        "or join our "
        "<a href=\"https://t.me/cs2_jesewe\" style=\"color: #D5006D; text-decoration: underline;\">Telegram channel</a>."
    )
    additional_info_text.setStyleSheet("font-size: 14px;")
    additional_info_text.setTextFormat(Qt.TextFormat.RichText)
    additional_info_text.setOpenExternalLinks(True)
    additional_info_text.setWordWrap(True)
    layout.addWidget(additional_info_text)

    # Bot control buttons
    main_window.start_button = QPushButton("Start Bot")
    main_window.stop_button = QPushButton("Stop Bot")
    main_window.start_button.clicked.connect(main_window.start_bot)
    main_window.stop_button.clicked.connect(main_window.stop_bot)

    buttons_layout = QHBoxLayout()
    buttons_layout.addWidget(main_window.start_button)
    buttons_layout.addWidget(main_window.stop_button)
    buttons_layout.setSpacing(20)

    layout.addWidget(main_window.status_label)
    layout.addWidget(main_window.last_update_label)
    layout.addLayout(buttons_layout)

    home_tab.setLayout(layout)
    main_window.tabs.addTab(home_tab, "Home")

def create_section_label(text, font_size):
    """Helper to create a styled section label."""
    label = QLabel(text)
    label.setStyleSheet(f"font-size: {font_size}px; font-weight: bold; color: #D5006D; margin-top: 10px;")
    return label