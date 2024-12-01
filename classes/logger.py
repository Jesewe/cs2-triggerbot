import os
import logging

class Logger:
    # Define the directory where logs will be stored.
    # Use an environment variable (%LOCALAPPDATA%) to ensure logs are stored in a user-specific location.
    LOG_DIRECTORY = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe\crashes')
    
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
        
        # Create or clear the log file to start fresh with each application run.
        with open(Logger.LOG_FILE, 'w') as f:
            pass  # Just opening the file in 'write' mode clears its contents.

        # Set up logging to output to both the log file and the console with INFO level or higher.
        logging.basicConfig(
            level=logging.INFO,  # Minimum logging level (INFO, WARNING, ERROR, etc.).
            format='[%(asctime)s %(levelname)s]: %(message)s',  # Standard log message format.
            handlers=[
                logging.FileHandler(Logger.LOG_FILE),  # Log to the specified file.
                logging.StreamHandler()  # Log to the console (stdout).
            ]
        )

    @staticmethod
    def get_logger():
        """
        Provides a logger instance to be used throughout the application.
        - This ensures a consistent logging setup in all parts of the code.
        - Returns a logger configured with the settings from `setup_logging`.
        """
        return logging.getLogger(__name__)  # Logger's name is set to the module name.