import os
import logging
from typing import ClassVar

class Logger:
    # Constants for log file configuration
    LOG_DIRECTORY: ClassVar[str] = os.path.expandvars(r'%LOCALAPPDATA%\Requests\ItsJesewe\crashes')
    LOG_FILE: ClassVar[str] = os.path.join(LOG_DIRECTORY, 'tb_logs.log')

    # Default log format
    _LOG_FORMAT: ClassVar[str] = '[%(asctime)s %(levelname)s]: %(message)s'
    
    @classmethod
    def setup_logging(cls) -> None:
        """
        Initializes application logging configuration.
        Creates log directory and file, configures handlers and formatting.
        """
        # Ensure log directory exists
        os.makedirs(cls.LOG_DIRECTORY, exist_ok=True)
        
        # Initialize empty log file
        open(cls.LOG_FILE, 'w').close()

        # Configure logging with file and console output
        logging.basicConfig(
            level=logging.INFO,
            format=cls._LOG_FORMAT,
            handlers=[
                logging.FileHandler(cls.LOG_FILE),
                logging.StreamHandler()
            ]
        )

    @classmethod 
    def get_logger(cls) -> logging.Logger:
        """
        Returns configured logger instance for application-wide use.
        
        Returns:
            logging.Logger: Logger instance with module name
        """
        return logging.getLogger(__name__)
