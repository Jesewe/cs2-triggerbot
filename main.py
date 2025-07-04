import sys

from classes.logger import Logger
from classes.config_manager import ConfigManager

from gui.main_window import MainWindow

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
        logger.debug("Application interrupted by user")
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        sys.exit(1)
    finally:
        logger.debug("Application shutting down")

if __name__ == "__main__":
    main()