import os
import logging
import traceback

class Logger:
    """
    A class to handle logging for the application.
    It sets up logging to a file, a detailed log file, and the console with enhanced error details.
    """
    # Define the directory where logs will be stored.
    LOG_DIRECTORY = os.path.expanduser(r'~\AppData\Local\Requests\ItsJesewe\crashes')
    # Define the full path for the log file within the LOG_DIRECTORY.
    LOG_FILE = os.path.join(LOG_DIRECTORY, 'vw_logs.log')
    # Define the full path for the detailed log file within the LOG_DIRECTORY.
    DETAILED_LOG_FILE = os.path.join(LOG_DIRECTORY, 'vw_detailed_logs.log')
    
    # Cache for the logger instance.
    _logger = None
    
    # Flag to prevent multiple logging setups
    _logger_configured = False

    @staticmethod
    def setup_logging():
        """
        Configures logging for the application.
        - Ensures the log directory exists.
        - Initializes the log files (clearing previous logs).
        - Sets up logging to write messages to both a brief log file, a detailed log file, and the console.
        """
        if Logger._logger_configured:
            return
        Logger._logger_configured = True
        
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(logging.DEBUG)

        # Ensure log directory exists
        try:
            os.makedirs(Logger.LOG_DIRECTORY, exist_ok=True)
        except Exception as e:
            print(f"Error creating log directory {Logger.LOG_DIRECTORY}: {e}")
            return  # Exit setup if directory creation fails

        # Standard formatter for brief logs and console
        standard_formatter = logging.Formatter(
            fmt='[%(asctime)s %(levelname)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler for vw_logs.log with error handling
        try:
            file_handler = logging.FileHandler(Logger.LOG_FILE, mode='w', encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(standard_formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Error setting up file handler for {Logger.LOG_FILE}: {e}")

        # Stream handler for console
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(standard_formatter)
        root_logger.addHandler(stream_handler)

        # Detailed formatter with enhanced error context
        detailed_formatter = logging.Formatter(
            fmt='[%(asctime)s.%(msecs)03d %(levelname)-8s] {%(name)s:%(module)s:%(funcName)s:%(lineno)d} [PID:%(process)d TID:%(thread)d] %(message)s%(exc_info)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        try:
            detailed_handler = logging.FileHandler(Logger.DETAILED_LOG_FILE, mode='w', encoding='utf-8')
            detailed_handler.setLevel(logging.DEBUG)
            detailed_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(detailed_handler)
        except Exception as e:
            print(f"Error setting up detailed handler for {Logger.DETAILED_LOG_FILE}: {e}")

        # Test log to verify setup
        logger = Logger.get_logger()
        logger.info("Logging system initialized successfully.")

    @staticmethod
    def get_logger():
        """Returns the cached logger instance, creating it if necessary."""
        if Logger._logger is None:
            Logger._logger = logging.getLogger(__name__)
        return Logger._logger

    @staticmethod
    def log_exception(exc: Exception, context: str = None):
        """Logs an exception with detailed information including stack trace and optional context."""
        logger_instance = Logger.get_logger()
        # Format the stack trace and exception details
        exc_details = f"\nException Type: {type(exc).__name__}\nException Message: {str(exc)}\nStack Trace:\n{''.join(traceback.format_tb(exc.__traceback__))}"
        if context:
            exc_details = f"Context: {context}\n{exc_details}"
        logger_instance.error(f"An exception occurred: {exc_details}", extra={'exc_info': ''})