import os
import logging
import traceback
import sys
import inspect

class SuppressErrorFilter(logging.Filter):
    def __init__(self, pattern):
        super().__init__()
        self.pattern = pattern

    def filter(self, record):
        if self.pattern in record.getMessage():
            return False
        return True

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
        suppress_filter = SuppressErrorFilter("Error drawing entity: 'NoneType' object is not subscriptable")
        stream_handler.addFilter(suppress_filter)
        root_logger.addHandler(stream_handler)

        # Detailed formatter with enhanced error context
        detailed_formatter = logging.Formatter(
            fmt='[%(asctime)s.%(msecs)03d %(levelname)-8s] {%(name)s:%(module)s:%(funcName)s:%(lineno)d} [PID:%(process)d TID:%(thread)d] %(message)s',
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
    def _get_caller_info():
        """Get detailed information about the caller including file, function, and line number."""
        frame = inspect.currentframe()
        try:
            # Go up the call stack to find the actual caller (skip _get_caller_info and log_exception)
            caller_frame = frame.f_back.f_back
            if caller_frame:
                filename = caller_frame.f_code.co_filename
                function_name = caller_frame.f_code.co_name
                line_number = caller_frame.f_lineno
                return {
                    'filename': os.path.basename(filename),
                    'full_path': filename,
                    'function': function_name,
                    'line': line_number
                }
        except:
            pass
        finally:
            del frame
        return None

    @staticmethod
    def _format_traceback_with_context(exc: Exception, context_lines: int = 3):
        """Format traceback with source code context around each frame."""
        tb_lines = []
        tb = exc.__traceback__
        
        while tb is not None:
            frame = tb.tb_frame
            filename = frame.f_code.co_filename
            line_number = tb.tb_lineno
            function_name = frame.f_code.co_name
            
            tb_lines.append(f"  File \"{filename}\", line {line_number}, in {function_name}")
            
            # Try to get source code context
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    source_lines = f.readlines()
                    
                start_line = max(0, line_number - context_lines - 1)
                end_line = min(len(source_lines), line_number + context_lines)
                
                for i in range(start_line, end_line):
                    line_content = source_lines[i].rstrip()
                    line_num = i + 1
                    if line_num == line_number:
                        tb_lines.append(f"    {line_num:4d} >>> {line_content}")
                    else:
                        tb_lines.append(f"    {line_num:4d}     {line_content}")
            except:
                # If we can't read the source, just show the line
                tb_lines.append(f"    <source unavailable>")
            
            tb_lines.append("")  # Empty line for readability
            tb = tb.tb_next
        
        return "\n".join(tb_lines)

    @staticmethod
    def log_exception(exc: Exception, context: str = None):
        """Logs an exception with detailed information including stack trace and optional context."""
        logger_instance = Logger.get_logger()
        
        # Get caller information
        caller_info = Logger._get_caller_info()
        
        # Get current exception info if not provided
        if exc is None:
            exc_type, exc_value, exc_tb = sys.exc_info()
            if exc_value:
                exc = exc_value
            else:
                logger_instance.error("log_exception called but no exception provided and no current exception")
                return
        
        # Format enhanced traceback with source context
        enhanced_traceback = Logger._format_traceback_with_context(exc)
        
        # Build detailed error message
        error_parts = []
        
        if context:
            error_parts.append(f"Context: {context}")
        
        if caller_info:
            error_parts.append(f"Called from: {caller_info['filename']}:{caller_info['line']} in {caller_info['function']}()")
        
        error_parts.extend([
            f"Exception Type: {type(exc).__name__}",
            f"Exception Message: {str(exc)}",
            f"Detailed Traceback with Source Context:",
            enhanced_traceback
        ])
        
        # Join all parts with newlines
        exc_details = "\n".join(error_parts)
        
        # Log the detailed error
        logger_instance.error(f"An exception occurred:\n{exc_details}")
        
        # Also log a brief version for console/standard log
        brief_message = f"{type(exc).__name__}: {str(exc)}"
        if caller_info:
            brief_message += f" (at {caller_info['filename']}:{caller_info['line']})"
        
        logger_instance.info(f"Exception: {brief_message}")

    @staticmethod
    def log_error_with_line(message: str, include_stack: bool = True):
        """Log an error message with automatic line number detection."""
        logger_instance = Logger.get_logger()
        caller_info = Logger._get_caller_info()
        
        if caller_info:
            enhanced_message = f"{message} (at {caller_info['filename']}:{caller_info['line']} in {caller_info['function']}())"
        else:
            enhanced_message = message
        
        if include_stack:
            # Get current stack trace
            stack_trace = ''.join(traceback.format_stack()[:-1])  # Exclude current frame
            enhanced_message += f"\nStack trace:\n{stack_trace}"
        
        logger_instance.error(enhanced_message)

    @staticmethod
    def log_warning_with_line(message: str):
        """Log a warning message with automatic line number detection."""
        logger_instance = Logger.get_logger()
        caller_info = Logger._get_caller_info()
        
        if caller_info:
            enhanced_message = f"{message} (at {caller_info['filename']}:{caller_info['line']} in {caller_info['function']}())"
        else:
            enhanced_message = message
        
        logger_instance.warning(enhanced_message)
