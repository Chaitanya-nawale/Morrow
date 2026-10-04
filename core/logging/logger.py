"""Structured logging setup for Morrow."""

import json
import logging
import sys
from typing import Any


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured machine-readable logs."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging(level: str = "INFO", log_format: str = "console") -> None:
    """Configure root logger with chosen formatting and handler."""
    root_logger = logging.getLogger()
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root_logger.setLevel(numeric_level)

    # Avoid adding duplicate handlers if setup is called multiple times
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    if log_format.lower() == "json":
        handler.setFormatter(JSONFormatter())
    else:
        console_fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt=console_fmt, datefmt="%Y-%m-%d %H:%M:%S"))

    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Retrieve named logger with standard project conventions."""
    return logging.getLogger(name)
