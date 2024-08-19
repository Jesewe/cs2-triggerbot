<div align="center">
   <img src="src/img/icon.png" alt="CS2 TriggerBot" width="200" height="200">
   <h1>🎯 CS2 TriggerBot 🎯</h1>
   <p>Your ultimate aiming assistant for Counter-Strike 2</p>
   <a href="#-features"><strong>Features</strong></a> •
   <a href="#-installation"><strong>Installation</strong></a> •
   <a href="#-usage"><strong>Usage</strong></a> •
   <a href="#-customization"><strong>Customization</strong></a> •
   <a href="#-troubleshooting"><strong>Troubleshooting</strong></a> •
   <a href="#-contributing"><strong>Contributing</strong></a>
</div>

---

# 🚀 Overview
CS2 TriggerBot is an automated tool designed for Counter-Strike 2 that assists with precise aiming by automatically triggering a mouse click when an enemy is detected in the player's crosshairs.

## ✨ Features
- **Automated Shooting:** Automatically triggers a mouse click when an enemy is detected.
- **Process Attachment:** Attaches to the `cs2.exe` process and reads memory values to make real-time decisions.
- **Customizable Trigger Key:** Allows users to define their own trigger key for activation.
- **Update Checker:** Automatically checks for the latest version and notifies the user if an update is available.
- **Error Logging:** Logs errors and important events to a log file for debugging purposes.

## ⚙️ Installation
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

## 🎮 Usage
1. Ensure that Counter-Strike 2 is running.
2. Execute the script using the command above.
3. The script will automatically check for updates and fetch the necessary offsets from the provided sources.
4. Once the script is running, press the configured trigger key (default: `X`) to activate the TriggerBot.
5. The tool will automatically simulate mouse clicks when an enemy is detected in the crosshairs.

## 🔧 Customization
- **Trigger Key:** You can change the trigger key by modifying the `TRIGGER_KEY` variable in the script.
- **Log Directory:** The log files are saved in the `%LOCALAPPDATA%\Requests\ItsJesewe\crashes` directory by default. You can change this by modifying the `LOG_DIRECTORY` variable.

## 🛠️ Troubleshooting
- **Failed to Fetch Offsets:** Ensure you have an active internet connection and that the source URLs are accessible.
- **Could Not Open `cs2.exe`:** Make sure the game is running and that you have the necessary permissions.
- **Unexpected Errors:** Check the log file located in the log directory for more details.

## 🤝 Contributing
Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/Jesewe/cs2-triggerbot).

## ⚠️ Disclaimer
This script is for educational purposes only. Using cheats or hacks in online games is against the terms of service of most games and can result in bans or other penalties. Use this script at your own risk.

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.