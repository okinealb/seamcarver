"""
Logging configuration for the seam carving project.
"""

import logging
import sys

class ColoredFormatter(logging.Formatter):
    """Add colors to CLI logging for better readability."""
    
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green  
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        if sys.stderr.isatty():  # Only colorize if terminal supports it
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

def setup_cli_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_file: str | None = None,
    color: bool = True
) -> None:
    """Configure logging for CLI usage.
    
    Args:
        verbose: Enable debug-level logging
        quiet: Only show warnings and errors
        log_file: Optional file to write detailed logs
        color: Use colored output (auto-detected for terminals)
    """
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Determine level
    if quiet:
        console_level = logging.WARNING
    elif verbose:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO
    
    # Console handler (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    
    # Format based on verbosity
    if verbose:
        console_format = '%(levelname)s: %(name)s: %(message)s'
    else:
        console_format = '%(message)s'
    
    # Apply formatter
    if color and sys.stderr.isatty():
        formatter = ColoredFormatter(console_format)
    else:
        formatter = logging.Formatter(console_format)
    
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_format = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        file_handler.setFormatter(logging.Formatter(
            file_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        file_handler.setLevel(logging.DEBUG)  # File gets everything
        root_logger.addHandler(file_handler)
    
    # Set root level
    root_logger.setLevel(logging.DEBUG)

def setup_library_logging(name: str) -> logging.Logger:
    """Configure logging for library usage."""
    logger = logging.getLogger(name)
    
    # Libraries should NOT configure the root logger
    # Add NullHandler to prevent "No handlers" warnings
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)