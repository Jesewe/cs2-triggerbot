from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from classes.config_manager import ConfigManager
from classes.utility import Utility

def init_general_settings_tab(main_window):
    """
    Sets up the General Settings tab for configuring the bot.
    Creates input fields and buttons, then attaches them to the main window.
    """
    general_settings_tab = QWidget()
    form_layout = QFormLayout()

    settings = main_window.bot.config.get('Settings', {})

    main_window.trigger_key_input = QLineEdit(settings.get('TriggerKey', ''))
    main_window.trigger_key_input.setToolTip("Set the key to activate the trigger bot (e.g., 'x' or 'x1' for mouse button 4, 'x2' for mouse button 5).")
    main_window.toggle_mode_checkbox = QCheckBox("Toggle Mode")
    main_window.toggle_mode_checkbox.setChecked(settings.get('ToggleMode', False))
    main_window.toggle_mode_checkbox.setToolTip("If checked, the trigger will toggle on/off with the trigger key.")
    main_window.min_delay_input = QLineEdit(str(settings.get('ShotDelayMin', 0.01)))
    main_window.min_delay_input.setToolTip("Minimum delay between shots in seconds (e.g., 0.01).")
    main_window.max_delay_input = QLineEdit(str(settings.get('ShotDelayMax', 0.1)))
    main_window.max_delay_input.setToolTip("Maximum delay between shots in seconds (must be >= Min Delay).")
    main_window.post_shot_delay_input = QLineEdit(str(settings.get('PostShotDelay', 0.1)))
    main_window.post_shot_delay_input.setToolTip("Delay after each shot in seconds (e.g., 0.1).")
    main_window.attack_teammates_checkbox = QCheckBox("Attack Teammates")
    main_window.attack_teammates_checkbox.setChecked(settings.get('AttackOnTeammates', False))
    main_window.attack_teammates_checkbox.setToolTip("If checked, the bot will attack teammates as well.")

    save_button = QPushButton("Save Config")
    save_button.setToolTip("Save the configuration settings to the configuration file.")
    save_button.clicked.connect(main_window.save_general_settings)
    open_config_button = QPushButton("Open Config Directory")
    open_config_button.setToolTip("Open the directory where the configuration file is stored.")
    open_config_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(ConfigManager.CONFIG_DIRECTORY)))

    checkbox_layout = QHBoxLayout()
    checkbox_layout.addWidget(main_window.toggle_mode_checkbox)
    checkbox_layout.addWidget(main_window.attack_teammates_checkbox)

    button_layout = QHBoxLayout()
    button_layout.addWidget(save_button)
    button_layout.addWidget(open_config_button)

    form_layout.addRow("Trigger Key:", main_window.trigger_key_input)
    form_layout.addRow(checkbox_layout)
    form_layout.addRow("Min Shot Delay:", main_window.min_delay_input)
    form_layout.addRow("Max Shot Delay:", main_window.max_delay_input)
    form_layout.addRow("Post Shot Delay:", main_window.post_shot_delay_input)
    form_layout.addItem(QSpacerItem(15, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    form_layout.addRow(button_layout)

    general_settings_tab.setLayout(form_layout)
    main_window.tabs.addTab(general_settings_tab, "General Settings")