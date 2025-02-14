import sys
from PyQt6.QtWidgets import QApplication

from classes.logger import Logger
from classes.main_window import MainWindow
from classes.trigger_bot import CS2TriggerBot

def main():
    # Set up logging for the application.
    Logger.setup_logging()
    logger = Logger.get_logger()

    # Initialize the QApplication. If an instance already exists, use it; otherwise, create a new one.
    app = QApplication.instance() or QApplication(sys.argv)

    # Log the loaded version.
    logger.info("Loaded version: %s", CS2TriggerBot.VERSION)

    # Create and display the main application window.
    window = MainWindow()
    window.show()

    # Start the application event loop and exit with the returned status.
    sys.exit(app.exec())

if __name__ == "__main__":
    main()