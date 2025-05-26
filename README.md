<div align="center">
   <img src="src/img/icon.png" alt="CS2 TriggerBot" width="200" height="200">
   <h1>CS2 TriggerBot</h1>
   <p>Your ultimate aiming assistant for Counter-Strike 2</p>

![Downloads](https://img.shields.io/github/downloads/jesewe/cs2-triggerbot/total?style=for-the-badge&logo=github&color=D5006D)
![Platforms](https://img.shields.io/badge/platform-Windows-blue?style=for-the-badge&logo=windows&color=D5006D)
![License](https://img.shields.io/github/license/jesewe/cs2-triggerbot?style=for-the-badge&color=D5006D)

<a href="#features"><strong>Features</strong></a> •
<a href="#installation"><strong>Installation</strong></a> •
<a href="#usage"><strong>Usage</strong></a> •
<a href="#configuration"><strong>Configuration</strong></a> •
<a href="#troubleshooting"><strong>Troubleshooting</strong></a> •
<a href="#contributing"><strong>Contributing</strong></a>

</div>

---

# Overview

CS2 TriggerBot is an automated tool designed for Counter-Strike 2 that assists with precise aiming by automatically triggering a mouse click when an enemy is detected in the player's crosshairs. The tool features a graphical user interface (GUI) for easy configuration.

## Features

- **Automatic Trigger**: Fires when an enemy is detected under your crosshair.
- **Configurable Trigger Key**: Set a keyboard key (e.g., `x`, `c`) or mouse button (`x1`, `x2`) via the GUI or `config.json`.
- **Toggle Mode**: Activate the bot with a single key press instead of holding (configurable in the GUI).
- **Configurable Delays**: Adjust minimum (`ShotDelayMin`), maximum (`ShotDelayMax`), and post-shot (`PostShotDelay`) delays for natural shooting behavior.
- **Attack Teammates Option**: Toggle friendly fire via a checkbox in the GUI or `config.json`.
- **Automatic Offset Fetching**: Retrieves the latest offsets and client data from remote sources on startup.
- **Graphical User Interface (GUI)**:
  - **Dashboard**: Monitor bot status, offset updates, and version info.
  - **Settings Tab**: Configure trigger settings and delays with real-time validation.
  - **Logs Tab**: View real-time logs from `%LOCALAPPDATA%\Requests\ItsJesewe\crashes\tb_logs.log`.
  - **FAQ Tab**: Access answers to common questions.
- **Dynamic Config Updates**: Detects and applies changes to `config.json` without restarting, thanks to `file_watcher.py`.
- **Share/Import Settings**: Export settings as a compressed code or import from others via the GUI.
- **Reset to Defaults**: Restore default settings with one click in the GUI.
- **Update Checker**: Alerts you to new versions via GitHub releases.
- **Logging**: Detailed logs saved to `%LOCALAPPDATA%\Requests\ItsJesewe\crashes\tb_logs.log` and a detailed version at `tb_detailed_logs.log`.

## Installation

You can install the trigger bot by cloning the repository or by downloading a pre-built executable file from the releases.

### Option 1: Clone the Repository

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

### Option 2: Download Pre-Built Executable

Alternatively, download the ready-to-use executable from the [Releases](https://github.com/jesewe/cs2-triggerbot/releases) page. Download the latest version and run the executable directly.

**Note:** This project requires Python version >= 3.8 and < 3.12.5.

## Configuration

The `config.json` file is automatically generated in the directory `%LOCALAPPDATA%\Requests\ItsJesewe\` on the first run. You can modify the `TriggerKey` in this file or via the GUI.

Example `config.json`:

```json
{
  "Settings": {
    "TriggerKey": "x",
    "ToggleMode": false,
    "ShotDelayMin": 0.01,
    "ShotDelayMax": 0.03,
    "AttackOnTeammates": false,
    "PostShotDelay": 0.1
  }
}
```

### Configuration Options

- **TriggerKey**: The key or mouse button (`x`, `x1`, or `x2`) to activate the bot.
- **ToggleMode**: `true` enables toggle mode; `false` requires holding the key.
- **ShotDelayMin** and **ShotDelayMax**: Control the delay between shots to simulate natural behavior.
- **PostShotDelay**: Delay after each shot (seconds).
- **AttackOnTeammates**: `true` to enable friendly fire.

**GUI Configuration:** Use the **Settings** tab to modify these values interactively. Changes are saved instantly and applied dynamically if `config.json` is edited externally.

## Usage

1. **Launch Counter-Strike 2:** Ensure the game is running.
2. **Start the Bot:** Run `main.py` or the executable, then click **Start Bot** in the Dashboard tab.
3. **Configure Settings:** Adjust trigger key, delays, and other options in the **Settings** tab.
4. **Monitor Activity:** Check the **Logs** tab for real-time updates or the **Dashboard** for status.
5. **Toggle the Bot:** Use the configured trigger key to activate/deactivate (toggle mode) or hold to fire (hold mode).
6. **Advanced Features:**
   - **Share/Import:** Export/import settings via the Settings tab.
   - **FAQ:** Refer to the FAQ tab for help.

## Troubleshooting

- **Failed to Fetch Offsets:** Ensure you have an active internet connection and that the source URLs are accessible.
- **Errors with Offsets after Game Update:** After a Counter-Strike 2 game update, there may be issues with offsets, which can result in errors. In this case, please wait for updated offsets to be released.
- **Could Not Open `cs2.exe`:** Make sure the game is running and that you have the necessary permissions.
- **Unexpected Errors:** Check the log file located in the log directory for more details.
- **Issues with Importing Settings:** Ensure the imported config.json file is valid and matches the expected format.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/Jesewe/cs2-triggerbot).

## Disclaimer

This script is for educational purposes only. Using cheats or hacks in online games is against the terms of service of most games and can result in bans or other penalties. Use this script at your own risk.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
