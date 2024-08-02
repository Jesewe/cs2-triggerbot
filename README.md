# Counter-Strike 2 TriggerBot

This is a simple TriggerBot for Counter-Strike 2. The TriggerBot automatically fires when the crosshair is on an enemy player. 

## Features

- Automatically shoots when aiming at an enemy.
- Uses offsets from a remote source to stay updated.
- Configurable trigger key.
- Logs activity and errors for easy debugging.

## Requirements

- Python 3.7+
- `pymem`
- `keyboard`
- `pynput`
- `requests`
- `pywin32`
- `packaging`

## Installation

1. Clone the repository or download the script.

   ```sh
   git clone https://github.com/Jesewe/cs2-triggerbot.git
   cd cs2-triggerbot
   ```

2. Install the required Python libraries.

   ```sh
   pip install pymem keyboard pynput requests pywin32 packaging
   ```

3. Run the script.

   ```sh
   python main.py
   ```

## Configuration

- **Trigger Key**: The default trigger key is `X`. You can change this by modifying the `triggerKey` variable in the script.
- **Application Name**: The default application name is set to `Counter-Strike 2`. Ensure this matches the window title of your game.

## Usage

1. Start Counter-Strike 2.
2. Run the `main.py` script.
3. Press and hold the trigger key (`X` by default) when your crosshair is on an enemy to automatically shoot.

## Code Overview

The script performs the following steps:

1. Fetches the latest offsets and client data from a remote source.
2. Initializes `Pymem` to access the game's memory.
3. Continuously checks if the game window is active and if the trigger key is pressed.
4. If the trigger key is pressed, reads the player's data and entity list from the game's memory.
5. If an enemy is detected under the crosshair, simulates a mouse click to shoot.

## Logging

The script logs important events and errors. The log includes timestamps and error messages, which can be helpful for debugging.

## Troubleshooting

- Ensure that Counter-Strike 2 is running and the window title matches `Counter-Strike 2`.
- Make sure you run the script with sufficient permissions to access the game's memory.
- Verify that the offsets are up to date. If the game updates, the offsets might change, and you will need to fetch the latest ones.

## Disclaimer

This script is for educational purposes only. Using cheats or hacks in online games is against the terms of service of most games and can result in bans or other penalties. Use this script at your own risk.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.