"""
Centralized logging configuration for HP12C calculator.
"""

import logging
import sys
from pathlib import Path


def setup_logging(
    log_level: int = logging.INFO,
    log_file: Path | None = None,
    log_format: str | None = None,
) -> logging.Logger:
    """Set up logging configuration for the application.

    Args:
        log_level: Logging level (default: INFO)
        log_file: Optional path to log file. If None, only console logging.
        log_format: Optional custom format string. If None, uses default format.

    Returns:
        Configured root logger instance.
    """
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - " "%(filename)s:%(lineno)d - %(message)s"
        )

    # Create formatter
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Get root logger
    logger = logging.getLogger("hp12c")
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file is provided)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__ of the calling module).

    Returns:
        Logger instance.
    """
    return logging.getLogger(f"hp12c.{name}")


# Initialize default logger on import
_default_logger = setup_logging()
