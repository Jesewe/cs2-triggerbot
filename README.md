# CS2 TriggerBot
This is a simple TriggerBot for Counter-Strike 2. The TriggerBot automatically fires when the crosshair is on an enemy player.

## Requirements
To run this project, you need to install the following Python modules:
- `pymem`
- `keyboard`
- `pywin32`
- `pynput`
- `requests`
- `packaging`
- `colorama`

## Installation
1. Clone the repository:
```bash
git clone https://github.com/Jesewe/cs2-triggerbot.git
```

2. Navigate to the project directory:
```bash
cd cs2-triggerbot
```

3. Install the required modules:
```bash
pip install -r requirements.txt
```

## Usage
To start the TriggerBot, run the script:
```bash
python main.py
```

## Configuration
By default, the TriggerBot uses the 'X' key to trigger. You can change the trigger key by modifying the `TRIGGER_KEY` variable in the script.

## Features
- Automatically detects enemies and triggers mouse clicks.
- Fetches the latest offsets from an online source.
- Checks for script updates and notifies the user if a new version is available.
- Logs all actions and errors to a specified log file and displays logs on the console.

## Logging
The TriggerBot logs all actions and errors in a log file located at `%LOCALAPPDATA%\Requests\ItsJesewe\crashes\logs.log`. The log file and directory are created automatically if they do not exist. 

## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## Disclaimer
This script is for educational purposes only. Using cheats or hacks in online games is against the terms of service of most games and can result in bans or other penalties. Use this script at your own risk.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.