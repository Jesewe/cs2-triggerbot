from PyQt6.QtWidgets import QApplication
import sys
from classes.logger import Logger
from classes.main_window import MainWindow
from classes.trigger_bot import CS2TriggerBot

# Entry point of the application
if __name__ == "__main__":
    # Set up the logging system for the application
    Logger.setup_logging()
    # Get the logger instance for the main module
    logger = Logger.get_logger()
    # Initialize the CS2TriggerBot object
    app = QApplication.instance() or QApplication(sys.argv)
    logger.info(f"Loaded version: {CS2TriggerBot.VERSION}")
    # Create and show the main application window
    window = MainWindow()
    window.show()
    # Execute the application event loop and exit on close
    app.exec()