import sys
from PyQt6.QtWidgets import QApplication
from classes.logger import Logger
from classes.main_window import MainWindow

# Entry point of the application
if __name__ == "__main__":
    # Set up the logging system for the application
    Logger.setup_logging()

    # Initialize the Qt application
    app = QApplication(sys.argv)

    # Create and show the main application window
    window = MainWindow()
    window.show()

    # Execute the application event loop and exit on close
    sys.exit(app.exec())
