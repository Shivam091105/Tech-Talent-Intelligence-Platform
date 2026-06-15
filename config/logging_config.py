"""
Logging configuration for the Tech Talent Intelligence Platform.
Provides a consistent logger with both console and file output.
"""

import logging
import sys
from pathlib import Path

from config.settings import PROJECT_ROOT, LOG_LEVEL


def setup_logger(name: str = "tech_talent") -> logging.Logger:
    """
    Create and return a configured logger.

    Args:
        name: Logger name (used to identify the source module).

    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    # Avoid adding handlers multiple times if called again
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
