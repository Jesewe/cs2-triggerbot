import os, logging

class Logger:
    # Define the directory where logs will be stored.
    # Use an environment variable (%LOCALAPPDATA%) to ensure logs are stored in a user-specific location.
    LOG_DIRECTORY = os.path.expanduser(r'~\AppData\Local\Requests\ItsJesewe\crashes')
    
    # Define the full path for the log file within the LOG_DIRECTORY.
    LOG_FILE = os.path.join(LOG_DIRECTORY, 'tb_logs.log')

    @staticmethod
    def setup_logging():
        """
        Configures logging for the application.
        - Ensures the log directory exists (creates it if necessary).
        - Initializes the log file (clears previous logs).
        - Sets up logging to write messages to both a file and the console.
        """
        # Create the log directory if it doesn't exist to avoid errors during file operations.
        os.makedirs(Logger.LOG_DIRECTORY, exist_ok=True)
        
        # Set up logging to output to both the log file and the console with INFO level or higher.
        logging.basicConfig(
            level=logging.INFO,  # Minimum logging level (INFO, WARNING, ERROR, etc.).
            format=f'[%(asctime)s %(levelname)s]: %(message)s',  # Standard log message format.
            handlers=[
                logging.FileHandler(Logger.LOG_FILE, mode='w'),  # Log to the specified file and clear it.
                logging.StreamHandler()  # Log to the console (stdout).
            ]
        )

    @staticmethod
    def get_logger():
        """
        Provides a logger instance to be used throughout the application.
        - This ensures a consistent logging setup in all parts of the code.
        - Returns a logger configured with the settings from `setup_logging`.

        Example usage:
        logger = Logger.get_logger()
        logger.info("This is an info message")
        """
        return logging.getLogger(__name__)  # Logger's name is set to the module name.
    
    @staticmethod
    def log_exception(exc: Exception):
        """
        Logs an exception with its traceback.
        - Use this method to capture exceptions in a standardized way.
        """
        logger = Logger.get_logger()
        logger.error("An exception occurred", exc_info=True)