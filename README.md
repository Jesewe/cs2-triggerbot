# CS2 TriggerBot

This Python script implements a TriggerBot for the game CS2 by modifying memory values to automatically shoot at enemies when the trigger key is pressed.

## Requirements
- Python 3.x
- `pymem` library
- `pynput` library
- `keyboard` library
- `win32gui` library
- `requests` library

## Installation
1. Install Python 3.x from the official website.
2. Install the required libraries using pip:
   ```bash
   pip install pymem pynput keyboard pywin32 requests
   ```

## Usage
1. Run the script in a Python environment.
2. The script will fetch necessary memory offsets and client data from GitHub.
3. Once started, the script will monitor the CS2 game window.
4. Press the defined trigger key (default is "X") while CS2 is in focus to activate the TriggerBot.
5. The TriggerBot will automatically shoot at enemies when the trigger key is pressed.
6. Adjustments to the delay timings for shooting can be made within the script (`time.sleep()` calls).
7. Press `Ctrl+C` to stop the script.

## Contributing

Contributions to the script are welcome.

## License

CS2 TriggerBot is released under the [MIT License](LICENSE).

## Disclaimer

The CS2 TriggerBot script is provided for educational purposes only. The author does not endorse cheating in any form, and this script should not be used to gain an unfair advantage in CS2 or any other game. Using this script may violate CS2's terms of service, resulting in penalties or a ban. Use it responsibly and at your own risk.