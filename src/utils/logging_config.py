"""Structured logging configuration for the application"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from .config import Config


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""

    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[Path] = None,
    json_format: bool = False
) -> logging.Logger:
    """
    Configure application-wide logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        json_format: Use JSON format for structured logging

    Returns:
        Root logger instance
    """
    level = level or Config.LOG_LEVEL
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Create root logger
    logger = logging.getLogger("litsearch")
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    if json_format:
        console_format = '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
    else:
        console_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'

    if not json_format and sys.stdout.isatty():
        console_handler.setFormatter(ColoredFormatter(console_format, datefmt='%Y-%m-%d %H:%M:%S'))
    else:
        console_handler.setFormatter(logging.Formatter(console_format, datefmt='%Y-%m-%d %H:%M:%S'))

    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        file_handler.setFormatter(logging.Formatter(file_format, datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("scholarly").setLevel(logging.WARNING)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (e.g., 'search.pubmed', 'retrieval.pdf')

    Returns:
        Logger instance
    """
    return logging.getLogger(f"litsearch.{name}")


# Initialize default logging on import
_root_logger = setup_logging()
