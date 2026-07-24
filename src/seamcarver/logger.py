"""
Logging configuration for the seam carving project.
"""

import copy
import logging
import sys


class ColoredFormatter(logging.Formatter):
    """Add colors to CLI logging for better readability."""

    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        if sys.stderr.isatty():  # Only colorize if terminal supports it
            record = copy.copy(record)
            color = self.COLORS.get(record.levelname, "")
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_cli_logging(
    verbose: bool = False,
    quiet: bool = False,
    log_file: str | None = None,
    color: bool = True,
) -> logging.Logger:
    """Configure logging for CLI usage.

    Args:
        verbose: Enable debug-level logging
        quiet: Only show warnings and errors
        log_file: Optional file to write detailed logs
        color: Use colored output (auto-detected for terminals)
    """
    logger = logging.getLogger("seamcarver.cli")
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

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
        console_format = "%(levelname)s: %(name)s: %(message)s"
    else:
        console_format = "%(message)s"

    # Apply formatter
    if color and sys.stderr.isatty():
        formatter = ColoredFormatter(console_format)
    else:
        formatter = logging.Formatter(console_format)

    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        file_handler.setFormatter(
            logging.Formatter(file_format, datefmt="%Y-%m-%d %H:%M:%S")
        )
        file_handler.setLevel(logging.DEBUG)  # File gets everything
        logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger
