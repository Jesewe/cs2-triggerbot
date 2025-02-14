import os, logging

class Logger:
    # Define the directory where logs will be stored.
    # Use an environment variable (%LOCALAPPDATA%) to ensure logs are stored in a user-specific location.
    LOG_DIRECTORY = os.path.expanduser(r'~\AppData\Local\Requests\ItsJesewe\crashes')
    
    # Define the full path for the log file within the LOG_DIRECTORY.
    LOG_FILE = os.path.join(LOG_DIRECTORY, 'tb_logs.log')

    # Define the full path for the detailed log file within the LOG_DIRECTORY.
    DETAILED_LOG_FILE = os.path.join(LOG_DIRECTORY, 'tb_detailed_logs.log')
    
    # Cache for the logger instance.
    _logger = None

    @staticmethod
    def setup_logging():
        """
        Configures logging for the application.
        - Ensures the log directory exists.
        - Initializes the log files (clearing previous logs).
        - Sets up logging to write messages to both a brief log file, a detailed log file, and the console.
        """
        # Ensure the log directory exists.
        os.makedirs(Logger.LOG_DIRECTORY, exist_ok=True)

        # Get the root logger and clear any existing handlers.
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.INFO)

        # Define the standard formatter for the brief logs and console.
        standard_formatter = logging.Formatter(
            fmt='[%(asctime)s %(levelname)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Create a file handler for the brief log file.
        file_handler = logging.FileHandler(Logger.LOG_FILE, mode='w')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(standard_formatter)
        root_logger.addHandler(file_handler)

        # Create a stream handler for console output.
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(standard_formatter)
        root_logger.addHandler(stream_handler)

        # Define a detailed formatter.
        detailed_formatter = logging.Formatter(
            fmt='[%(asctime)s %(levelname)s {%(module)s : %(funcName)s} (%(lineno)d)]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Create a file handler for detailed logging.
        detailed_handler = logging.FileHandler(Logger.DETAILED_LOG_FILE, mode='w')
        detailed_handler.setLevel(logging.INFO)
        detailed_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(detailed_handler)

    @staticmethod
    def get_logger():
        """
        Provides a logger instance for use throughout the application.
        Returns:
            logging.Logger: A logger configured with the settings from `setup_logging`.
        """
        if Logger._logger is None:
            Logger._logger = logging.getLogger(__name__)
        return Logger._logger

    @staticmethod
    def log_exception(exc: Exception):
        """
        Logs an exception along with its traceback.
        Use this method to capture exceptions in a standardized way.
        """
        logger_instance = Logger.get_logger()
        logger_instance.error("An exception occurred", exc_info=True)
