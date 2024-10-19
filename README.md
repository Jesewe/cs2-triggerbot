<div align="center">
   <img src="src/img/icon.png" alt="CS2 TriggerBot" width="200" height="200">
   <h1>🎯 CS2 TriggerBot 🎯</h1>
   <p>Your ultimate aiming assistant for Counter-Strike 2</p>
   <a href="#features"><strong>Features</strong></a> •
   <a href="#installation"><strong>Installation</strong></a> •
   <a href="#usage"><strong>Usage</strong></a> •
   <a href="#customization"><strong>Customization</strong></a> •
   <a href="#troubleshooting"><strong>Troubleshooting</strong></a> •
   <a href="#contributing"><strong>Contributing</strong></a>
</div>

---

# Overview
CS2 TriggerBot is an automated tool designed for Counter-Strike 2 that assists with precise aiming by automatically triggering a mouse click when an enemy is detected in the player's crosshairs.

## Features
- **Automatic Trigger**: Fires your weapon when an enemy is detected under your crosshair.
- **Configurable Trigger Key**: You can configure the trigger key through the `config.ini` file. By default, the side mouse button (MOUSE 5) is used.
- **Offsets and Client Data**: Fetches the latest offsets and client data automatically from remote sources.
- **Logging**: Detailed logs are saved in `%LOCALAPPDATA%\Requests\ItsJesewe\crashes\tb_logs.log`.
- **Update Checker**: Automatically checks for updates from the GitHub repository.

## Installation
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/Jesewe/cs2-triggerbot.git
   cd cs2-triggerbot
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Script:**
   ```bash
   python main.py
   ```

## Obfuscating and Compiling
1. **Install Required Packages**
   ```bash
   pip install pyinstaller pyarmor
   ```
2. **Generate Obfuscated Files**
   Navigate to the directory containing all scripts
   ```bash
   cd cs2-triggerbot
   ```
   and run:
   
   ```bash
   pyarmor gen --pack onefile main.py
   ```
4. **Rename the Output File**
   Rename the resulting ```dist/main.exe``` file and use it.

## Configuration
The `config.ini` file is automatically generated in the directory `%LOCALAPPDATA%\Requests\ItsJesewe\` on the first run. You can modify the `TriggerKey` in this file to change the key that activates the bot. The default key is set to `x2` (MOUSE 5).

Example `config.ini`:
```ini
[Settings]
TriggerKey = x2
ShotDelayMin = 0.01
ShotDelayMax = 0.03

[Logger]
LogLevel = INFO
```

## Usage
- Launch Counter-Strike 2.
- Run the TriggerBot using the command mentioned above.
- The bot will automatically start functioning when the game is active.

## Troubleshooting
- **Failed to Fetch Offsets:** Ensure you have an active internet connection and that the source URLs are accessible.
- **Could Not Open `cs2.exe`:** Make sure the game is running and that you have the necessary permissions.
- **Unexpected Errors:** Check the log file located in the log directory for more details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/Jesewe/cs2-triggerbot).

## Disclaimer
This script is for educational purposes only. Using cheats or hacks in online games is against the terms of service of most games and can result in bans or other penalties. Use this script at your own risk.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.