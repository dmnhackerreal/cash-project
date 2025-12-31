# -*- coding: utf-8 -*-
"""
Advanced logging system
Advanced logging system for Trading Tool
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config import Config

class CustomFormatter(logging.Formatter):
    """Custom formatter for logs"""
    
    # Terminal colors
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m'  # Purple
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Format log record"""
        # Add colors
        if sys.stdout.isatty():  # Only if terminal
            color = self.COLORS.get(record.levelname, self.RESET)
            record.levelname = f"{color}{record.levelname}{self.RESET}"
            record.name = f"\033[90m{record.name}{self.RESET}"
        
        return super().format(record)

def setup_logger(name: str, level: str = None) -> logging.Logger:
    """
    Setup and return a logger
    
    Parameters:
        name (str): Logger name
        level (str): Logging level
    
    Returns:
        logging.Logger: Logger object
    """
    if level is None:
        level = Config.LOG.LOG_LEVEL
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Prevent duplicate logging
    if logger.handlers:
        return logger
    
    # Log format
    formatter = CustomFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler (with rotation)
    file_handler = RotatingFileHandler(
        Config.LOG.LOG_FILE,
        maxBytes=Config.LOG.MAX_LOG_SIZE,
        backupCount=Config.LOG.BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(Config.LOG.LOG_FORMAT))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_function_call(func):
    """Decorator for logging function calls"""
    def wrapper(*args, **kwargs):
        logger = setup_logger(func.__module__)
        
        # Log input
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            # Log output
            logger.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    
    return wrapper

def log_performance(func):
    """Decorator for logging execution time"""
    import time
    
    def wrapper(*args, **kwargs):
        logger = setup_logger(func.__module__)
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return wrapper

class LogMixin:
    """Mixin class for adding logging to classes"""
    
    def __init__(self):
        self._logger = setup_logger(self.__class__.__name__)
    
    @property
    def logger(self):
        """Access logger"""
        return self._logger
    
    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
    
    def log_error(self, message: str, exc_info: bool = False):
        """Log error message"""
        self.logger.error(message, exc_info=exc_info)
    
    def log_debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)

def test_logging():
    """Test logging function"""
    logger = setup_logger("test")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

if __name__ == "__main__":
    test_logging()
