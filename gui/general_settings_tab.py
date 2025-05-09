import orjson, base64, zlib

from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, QDialog, QVBoxLayout, QLabel, QTextEdit, QApplication
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl, Qt

from classes.config_manager import ConfigManager
from classes.utility import Utility

class ShareImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Share/Import Settings")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Label and text area for code input/output
        self.label = QLabel("Enter code to import or generate code to share:")
        self.code_input = QTextEdit()
        self.code_input.setFixedHeight(100)

        # Buttons
        self.import_button = QPushButton("Import Settings")
        self.export_button = QPushButton("Generate and Copy Code")
        
        # Button connections
        self.import_button.clicked.connect(self.import_settings)
        self.export_button.clicked.connect(self.export_settings)

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.code_input)
        layout.addWidget(self.import_button)
        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def export_settings(self):
        # Gather current settings
        settings = {
            'TriggerKey': self.parent().trigger_key_input.text(),
            'ToggleMode': self.parent().toggle_mode_checkbox.isChecked(),
            'ShotDelayMin': float(self.parent().min_delay_input.text() or 0.01),
            'ShotDelayMax': float(self.parent().max_delay_input.text() or 0.1),
            'PostShotDelay': float(self.parent().post_shot_delay_input.text() or 0.1),
            'AttackOnTeammates': self.parent().attack_teammates_checkbox.isChecked()
        }
        
        # Serialize to JSON, compress with zlib, and encode to base64
        json_bytes = orjson.dumps(settings)
        compressed = zlib.compress(json_bytes)
        encoded = base64.b64encode(compressed).decode()
        code = f"TB-{encoded}"
        
        # Copy to clipboard using QApplication
        clipboard = QApplication.instance().clipboard()
        clipboard.setText(code)
        
        # Show in text area and notify user
        self.code_input.setText(code)
        self.label.setText("Code copied to clipboard!")

    def import_settings(self):
        code = self.code_input.toPlainText().strip()
        if not code.startswith("TB-"):
            self.label.setText("Invalid code format. Must start with 'TB-'")
            return
        
        # Decode, decompress, and apply settings
        try:
            encoded = code[3:]
            compressed = base64.b64decode(encoded)
            json_bytes = zlib.decompress(compressed)
            settings = orjson.loads(json_bytes)
            
            # Apply settings to UI
            main_window = self.parent()
            main_window.trigger_key_input.setText(settings.get('TriggerKey', ''))
            main_window.toggle_mode_checkbox.setChecked(settings.get('ToggleMode', False))
            main_window.min_delay_input.setText(str(settings.get('ShotDelayMin', 0.01)))
            main_window.max_delay_input.setText(str(settings.get('ShotDelayMax', 0.1)))
            main_window.post_shot_delay_input.setText(str(settings.get('PostShotDelay', 0.1)))
            main_window.attack_teammates_checkbox.setChecked(settings.get('AttackOnTeammates', False))
            
            # Save the imported settings using the module function
            save_general_settings(main_window)
            
            self.label.setText("Settings imported and saved successfully!")
        except Exception as e:
            self.label.setText(f"Error importing settings: {str(e)}")

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
    save_button.clicked.connect(lambda: save_general_settings(main_window))
    open_config_button = QPushButton("Open Config Directory")
    open_config_button.setToolTip("Open the directory where the configuration file is stored.")
    open_config_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(ConfigManager.CONFIG_DIRECTORY)))
    share_import_button = QPushButton("Share/Import")
    share_import_button.setToolTip("Open a dialog to share or import settings.")
    share_import_button.clicked.connect(lambda: ShareImportDialog(main_window).exec())
    reset_button = QPushButton("Reset to Defaults")
    reset_button.setToolTip("Reset all settings to their default values.")
    reset_button.clicked.connect(lambda: reset_to_defaults(main_window))

    # First checkbox layout for Toggle Mode and Attack Teammates
    checkbox_layout_1 = QHBoxLayout()
    checkbox_layout_1.addWidget(main_window.toggle_mode_checkbox)
    checkbox_layout_1.addWidget(main_window.attack_teammates_checkbox)

    button_layout = QHBoxLayout()
    button_layout.addWidget(save_button)
    button_layout.addWidget(open_config_button)
    button_layout.addWidget(share_import_button)
    button_layout.addWidget(reset_button)

    form_layout.addRow("Trigger Key:", main_window.trigger_key_input)
    form_layout.addRow(checkbox_layout_1)
    form_layout.addRow("Min Shot Delay:", main_window.min_delay_input)
    form_layout.addRow("Max Shot Delay:", main_window.max_delay_input)
    form_layout.addRow("Post Shot Delay:", main_window.post_shot_delay_input)
    form_layout.addItem(QSpacerItem(15, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    form_layout.addRow(button_layout)

    general_settings_tab.setLayout(form_layout)
    main_window.tabs.addTab(general_settings_tab, "General Settings")

def save_general_settings(main_window):
    """
    Saves the user's changes to the bot's configuration:
    - Validates user inputs.
    - Updates the bot's configuration with new values.
    - Persists the updated configuration using the ConfigManager.
    """
    try:
        validate_inputs(main_window)
        settings = main_window.bot.config['Settings']
        settings['TriggerKey'] = main_window.trigger_key_input.text().strip()
        settings['ToggleMode'] = main_window.toggle_mode_checkbox.isChecked()
        settings['AttackOnTeammates'] = main_window.attack_teammates_checkbox.isChecked()
        settings['ShotDelayMin'] = float(main_window.min_delay_input.text())
        settings['ShotDelayMax'] = float(main_window.max_delay_input.text())
        settings['PostShotDelay'] = float(main_window.post_shot_delay_input.text())
        ConfigManager.save_config(main_window.bot.config)
        main_window.bot.update_config(main_window.bot.config)
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(main_window, "Settings Saved", "Configuration has been successfully saved.")
    except ValueError as e:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(main_window, "Invalid Input", str(e))

def validate_inputs(main_window):
    """
    Validates user input fields in the General Settings tab.
    Ensures all required fields have valid values.
    """
    trigger_key = main_window.trigger_key_input.text().strip()
    if not trigger_key:
        raise ValueError("Trigger key cannot be empty.")

    try:
        min_delay = float(main_window.min_delay_input.text().strip())
        max_delay = float(main_window.max_delay_input.text().strip())
        post_delay = float(main_window.post_shot_delay_input.text().strip())
    except ValueError:
        raise ValueError("Delay values must be valid numbers.")

    if min_delay < 0 or max_delay < 0 or post_delay < 0:
        raise ValueError("Delay values must be non-negative.")
    if min_delay > max_delay:
        raise ValueError("Minimum delay cannot be greater than maximum delay.")
    
def reset_to_defaults(main_window):
    """
    Resets all settings in the General Settings tab to their default values
    as defined in ConfigManager.DEFAULT_CONFIG, then сохраняет их.
    """
    defaults = ConfigManager.DEFAULT_CONFIG['Settings']

    main_window.trigger_key_input.setText(defaults.get('TriggerKey', ''))
    main_window.toggle_mode_checkbox.setChecked(defaults.get('ToggleMode', False))
    main_window.min_delay_input.setText(str(defaults.get('ShotDelayMin', 0.01)))
    main_window.max_delay_input.setText(str(defaults.get('ShotDelayMax', 0.1)))
    main_window.post_shot_delay_input.setText(str(defaults.get('PostShotDelay', 0.1)))
    main_window.attack_teammates_checkbox.setChecked(defaults.get('AttackOnTeammates', False))

    save_general_settings(main_window)