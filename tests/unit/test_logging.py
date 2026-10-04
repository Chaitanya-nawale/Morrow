"""Unit tests for structured logging functionality."""

import logging

from core.logging.logger import JSONFormatter, get_logger, setup_logging


def test_get_logger() -> None:
    """Verify named logger instantiation."""
    logger = get_logger("test.component")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test.component"


def test_setup_logging_console() -> None:
    """Verify setup_logging configures root logger with console formatter."""
    setup_logging(level="DEBUG", log_format="console")
    root = logging.getLogger()
    assert root.level == logging.DEBUG
    assert len(root.handlers) >= 1


def test_setup_logging_json() -> None:
    """Verify setup_logging configures root logger with JSONFormatter."""
    setup_logging(level="INFO", log_format="json")
    root = logging.getLogger()
    assert root.level == logging.INFO
    assert len(root.handlers) >= 1
    assert isinstance(root.handlers[0].formatter, JSONFormatter)


def test_json_formatter_output() -> None:
    """Verify JSONFormatter produces valid structured JSON string."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Sample log message: %s",
        args=("success",),
        exc_info=None,
    )
    output = formatter.format(record)
    assert '"level": "INFO"' in output
    assert '"message": "Sample log message: success"' in output
    assert '"timestamp"' in output
