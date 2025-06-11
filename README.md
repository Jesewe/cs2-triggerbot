<div align="center">
   <img src="src/img/icon.png" alt="CS2 TriggerBot" width="200" height="200">
   <h1>CS2 TriggerBot</h1>
   <p>Your ultimate aiming assistant for Counter-Strike 2</p>

[![Downloads](https://img.shields.io/github/downloads/jesewe/cs2-triggerbot/total?style=for-the-badge&logo=github&color=D5006D)](https://github.com/Jesewe/cs2-triggerbot/releases)
[![Latest Release](https://img.shields.io/github/v/release/jesewe/cs2-triggerbot?style=for-the-badge&logo=github&color=D5006D)](https://github.com/Jesewe/cs2-triggerbot/releases/latest/)
[![License](https://img.shields.io/github/license/jesewe/cs2-triggerbot?style=for-the-badge&color=D5006D)](LICENSE)
[![Boosty](https://img.shields.io/badge/Support%20on-Boosty-orange?style=for-the-badge&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABx0lEQVQ4T2NkoBAwUqifgXH7Hz7++X/sXz1yF8Rz9V6QCBhYMBFAEgnk6sDkNf/XlDPf/2nqgM7iXvb57+3V+c1sbmF9AvHPnz/ff39lQUTtPzj0YPvj79u1Pnjx58P///v2rf/75u08cOhR3+vPnT///+OP79+/d3TiBtHR1d/fXv35+8ffv2tc+fP5xAiPu7N0YmJiZs/f37/3/1/5BgYGBgYGevn27evfuHYNzc3P79OmTz5w5I0BcXFw//vjjc+7cOT179mx2GoQxgqYO/vn0zMzOjv78/nT59+oSpqam5e/bsmXfv3pVVVVUjlUdf369ZOTk/Px8YOrq6hoyMjIpKSkxZs2axZIlS9y5cyc1NTUuXLhgbm7u9u3b9evXr5WVlXn69GkFBQW+efNmRUVFLVu2zOrqKhwcHLp48aIqKiq6e/duMTExMXDgQHBwcFD9+/c3b968I0eOHGzatEkJCQlp0qQJjY2Nt956KXDhwoVFixY1dOjQoTfeeIPq6uqWnZ2dCgsLU1FR0QULFkxKSkq+fv1q3759x44dO2zYsIGioqJLly7Vv39/ZWVlRUVF5+vTp8fPz2xYsWqK+vP/78+QqFQrZs2bLCwsLZ2dlRqVQ5ZcqUbN++vZUrV+Tn5xcuXKj8+fPVr18//v7778yYMSMbNmyQkpIiJSUFjY2NDh06tPz8/ISEhCgqKtHLlyiVLlqT8/Py8efOmadOmOT09fWzatEnnzp1TKBRlZ2fXrl3r1q1bYWFhQUxMzPKysr279//zpw5U+3bt7e+vr5hYWFOnz+vRYsWWrNmjWvXrjUnT57k5OSUlpZGc3Oz69evNzMzUvn17Tpw4UauXL2dmZpKTk7V9+/a2bNmihYUFxcXFGz16dC5fvjxt27aVkpJihw8fDgYGBnJzc2XKlCFjxozh4eFdu3YtNjY2nTp1ymq1WlFRUfr06VOXLl1UqVTi5eXFvXv3+/fvX5s2bcqSJUs0btyYLVu2dOTIEYODg7Vu3Zrbtm1DhgzRq1cvnTt3jqSkJO3Zs0cVFhbq1KnDyMgYLVq0sNixY/Lz82PYsGEaP36c8ePHmTNnDpWVlXn48GG1atWqmTNnioqKkiNHjtjZ2dn69euZmZnR1NSU7du3V3Nzs9asWSNOnDiR3NxcBwcH66xXkP89rZhLhAAAAAElFTkSuQmCC)](https://boosty.to/jesewe)

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
- **Configurable Trigger Key**: Set a keyboard key (e.g., `x`, `c`) or mouse button (`mouse4`, `mouse5`) via the GUI or `config.json`.
- **Toggle Mode**: Activate the bot with a single key press instead of holding (configurable in the GUI).
- **Configurable Delays**: Adjust minimum (`ShotDelayMin`), maximum (`ShotDelayMax`), and post-shot (`PostShotDelay`) delays for natural shooting behavior.
- **Attack Teammates Option**: Toggle friendly fire via a checkbox in the GUI or `config.json`.
- **Automatic Offset Fetching**: Retrieves the latest offsets and client data from remote sources on startup.
- **Graphical User Interface (GUI)**:
  - **Dashboard**: Monitor bot status, offset updates, and version info.
  - **Settings Tab**: Configure trigger settings and delays with real-time validation.
  - **Logs Tab**: View real-time logs from `%LOCALAPPDATA%\Requests\ItsJesewe\crashes\tb_logs.log`.
  - **FAQ Tab**: Access answers to common questions.
  - **Supporters Tab**: View a list of contributors and supporters who help the project.
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

- **TriggerKey**: The key or mouse button (`x`, `mouse4`, or `mouse5`) to activate the bot.
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
- **Errors with Offsets after Game Update:** After a Counter-Strike 2 game update, there may be issues with offsets, which can result in errors. Offsets are sourced from [https://github.com/a2x/cs2-dumper](https://github.com/a2x/cs2-dumper) and are not updated by the author of TriggerBot. Please wait for updated offsets to be released by the cs2-dumper repository.
- **Could Not Open `cs2.exe`:** Make sure the game is running and that you have the necessary permissions.
- **Unexpected Errors:** Check the log file located in the log directory for more details.
- **Issues with Importing Settings:** Ensure the imported config.json file is valid and matches the expected format.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/Jesewe/cs2-triggerbot).

## Support the Developer

If you find CS2 TriggerBot helpful and want to support its continued development, consider donating through Boosty. Your support helps maintain and improve this tool.

- [Support on Boosty](https://boosty.to/jesewe)

Thank you for your generosity!

## Disclaimer

This script is for educational purposes only. Using cheats or hacks in online games is against the terms of service of most games and can result in bans or other penalties. Use this script at your own risk.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
