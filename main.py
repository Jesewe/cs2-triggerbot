import sys

from classes.logger import Logger
from gui.main_window import MainWindow
from classes.config_manager import ConfigManager

def main():
    # Set up logging for the application.
    Logger.setup_logging()
    logger = Logger.get_logger()

    # Log the loaded version.
    logger.info("Loaded version: %s", ConfigManager.VERSION)

    try:
        # Create and run the main application window.
        window = MainWindow()
        window.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        sys.exit(1)
    finally:
        logger.info("Application shutting down")

if __name__ == "__main__":
    main()