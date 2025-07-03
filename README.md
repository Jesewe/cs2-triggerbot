<div align="center">
   <img src="src/img/icon.png" alt="VioletWing" width="200" height="200">
   <h1>VioletWing</h1>
   <p>Your ultimate assistant for Counter-Strike 2</p>

[![Downloads](https://img.shields.io/github/downloads/jesewe/VioletWing/total?style=for-the-badge&logo=github&color=D5006D)](https://github.com/Jesewe/VioletWing/releases)
[![Latest Release](https://img.shields.io/github/v/release/jesewe/VioletWing?style=for-the-badge&logo=github&color=D5006D)](https://github.com/Jesewe/VioletWing/releases/latest/)
[![License](https://img.shields.io/github/license/jesewe/VioletWing?style=for-the-badge&color=D5006D)](LICENSE)
[![Boosty](https://img.shields.io/badge/Support%20on-Boosty-orange?style=for-the-badge&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABx0lEQVQ4T2NkoBAwUqifgXH7Hz7++X/sXz1yF8Rz9V6QCBhYMBFAEgnk6sDkNf/XlDPf/2nqgM7iXvb57+3V+c1sbmF9AvHPnz/ff39lQUTtPzj0YPvj79u1Pnjx58P///v2rf/75u08cOhR3+vPnT///+OP79+/d3TiBtHR1d/fXv35+8ffv2tc+fP5xAiPu7N0YmJiZs/f37/3/1/5BgYGBgYGevn27evfuHYNzc3P79OmTz5w5I0BcXFw//vjjc+7cOT179mx2GoQxgqYO/vn0zMzOjv78/nT59+oSpqam5e/bsmXfv3pVVVVUjlUdf369ZOTk/Px8YOrq6hoyMjIpKSkxZs2axZIlS9y5cyc1NTUuXLhgbm7u9u3b9evXr5WVlXn69GkFBQW+efNmRUVFLVu2zOrqKhwcHLp48aIqKiq6e/duMTExMXDgQHBwcFD9+/c3b968I0eOHGzatEkJCQlp0qQJjY2Nt956KXDhwoVFixY1dOjQoTfeeIPq6uqWnZ2dCgsLU1FR0QULFkxKSkq+fv1q3759x44dO2zYsIGioqJLly7Vv39/ZWVlRUVF5+vTp8fPz2xYsWqK+vP/78+QqFQrZs2bLCwsLZ2dnRqVQ5ZcqUbN++vZUrV+Tn5xcuXKj8+fPVr18//v7778yYMSMbNmyQkpIiJSUFjY2NDh06tPz8/ISEhCgqKtHLlyiVLlqT8/Pzy8efOmadOmOT09fWzatEnnzp1TKBRlZ2fXrl3r1q1bYWFhQUxMzPKysr279//zpw5U+3bt7e+vr5hYWFOnz+vRYsWWrNmjWvXrjUnT57k5OSUlpZGc3Oz69evNzMzUvn17Tpw4UauXL2dmZpKTk7V9+/a2bNmihYUFxcXFGz16dC5fvjxt27aVkpJihw8fDgYGBnJzc2XKlCFjxozh4eFdu3YtNjY2nTp1ymq1WlFRUfr06VOXLl1UqVTi5eXFvXv3+/fvX5s2bcqSJUs0btyYLVu2dOTIEYODg7Vu3Zrbtm1DhgzRq1cvnTt3jqSkJO3Zs0cVFhbq1KnDyMgYLVq0sNixY/Lz82PYsGEaP36c8ePHmTNnDpWVlXn48GG1atWqmTNnioqKkiNHjtjZ2dn69euZmZnR1NSU7du3V3Nzs9asWSNOnDiR3NxcBwcH66xXkP89rZhLhAAAAAElFTkSuQmCC)](https://boosty.to/jesewe/donate)

<a href="#features"><strong>Features</strong></a> •
<a href="#installation"><strong>Installation</strong></a> •
<a href="#usage"><strong>Usage</strong></a> •
<a href="#troubleshooting"><strong>Troubleshooting</strong></a> •
<a href="#contributing"><strong>Contributing</strong></a>

</div>

---

# Overview

VioletWing is an automated tool designed for Counter-Strike 2 that enhances gameplay with features like precise aiming, visual overlays, and movement automation. It includes a graphical user interface (GUI) for easy configuration.

## Features

- **TriggerBot**:
  - Automatically fires when an enemy is under your crosshair.
  - Configurable trigger key (e.g., `x`, `c`, `mouse4`, `mouse5`) via GUI or `config.json`.
  - Toggle mode for single-key activation.
  - Adjustable delays (`ShotDelayMin`, `ShotDelayMax`, `PostShotDelay`) for natural shooting.
  - Option to attack teammates.
- **Overlay (ESP)**:
  - Displays enemy bounding boxes, snaplines, health numbers, nicknames, and a minimap.
  - Customizable colors, line thickness, and minimap size.
- **Bunnyhop**:
  - Automates bunny hopping for continuous jumping and speed maintenance.
- **NoFlash**:
  - Reduces or eliminates flashbang effects for uninterrupted visibility.
- **Automatic Offset Fetching**: Retrieves latest offsets from remote sources on startup.
- **Graphical User Interface (GUI)**:
  - **Dashboard**: Shows bot status, offset updates, and version info.
  - **General Settings**: Toggle TriggerBot, Overlay, Bunnyhop, and NoFlash.
  - **Trigger Settings**: Configure trigger key, delays, and toggle mode.
  - **Overlay Settings**: Adjust ESP features and appearance.
  - **Logs Tab**: View real-time logs from `%LOCALAPPDATA%\Requests\ItsJesewe\crashes\vw_logs.log`.
  - **FAQ Tab**: Answers to common questions about all features.
  - **Supporters Tab**: Lists contributors and supporters.
- **Dynamic Config Updates**: Applies `config.json` changes without restarting via `file_watcher.py`.
- **Update Checker**: Notifies of new versions via GitHub releases.
- **Logging**: Saves logs to `%LOCALAPPDATA%\Requests\ItsJesewe\crashes\vw_logs.log` and `vw_detailed_logs.log`.

## Installation

Install by cloning the repository or downloading a pre-built executable from releases.

### Option 1: Clone the Repository

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Jesewe/VioletWing.git
   cd VioletWing
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   **PyMeow Module:**  
    PyMeow is essential for rendering the overlay.  
    Download the latest `pyMeow*.zip` from the [PyMeow GitHub Releases page](https://github.com/qb-0/pyMeow/releases) and install it:

   ```bash
   pip install pyMeow*.zip
   ```

3. **Run the Script:**

   ```bash
   python main.py
   ```

### Option 2: Download Pre-Built Executable

Download the latest executable from the [Releases](https://github.com/Jesewe/VioletWing/releases) page and run it directly.

**Note:** Requires Python >= 3.8 and < 3.12.5.

## Troubleshooting

- **Failed to Fetch Offsets**: Verify internet connection and source URL accessibility.
- **Offset Errors Post-Update**: Wait for updated offsets from [https://github.com/a2x/cs2-dumper](https://github.com/a2x/cs2-dumper).
- **Could Not Open `cs2.exe`**: Ensure the game is running with necessary permissions.
- **Overlay Not Displaying**: Check Overlay settings and game mode (windowed/borderless).
- **Bunnyhop Inconsistent**: Verify focus on game window and settings.
- **NoFlash Not Working**: Confirm offsets are updated and feature is enabled.
- **Unexpected Errors**: Review logs in `%LOCALAPPDATA%\Requests\ItsJesewe\crashes\`.
- **Invalid Config Import**: Ensure `config.json` format is correct.

## Contributing

Contributions are welcome! Open an issue or submit a pull request on the [GitHub repository](https://github.com/Jesewe/VioletWing).

## Support the Developer

Support continued development by donating via Boosty:

- [Support on Boosty](https://boosty.to/jesewe/donate)

Thank you for your support!

## Disclaimer

This tool is for educational purposes only. Using automation tools in online games violates terms of service and may result in bans. Use at your own risk.

## License

Licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
