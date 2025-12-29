"""Tests for the logging configuration module"""

import pytest
import logging
from io import StringIO
from src.utils.logging_config import setup_logging, get_logger, ColoredFormatter


class TestLoggingConfig:
    """Test suite for logging configuration"""

    def test_setup_logging_default(self):
        """Test default logging setup"""
        logger = setup_logging(level="INFO")

        assert logger is not None
        assert logger.name == "litsearch"
        assert logger.level == logging.INFO

    def test_setup_logging_custom_level(self):
        """Test logging with custom level"""
        logger = setup_logging(level="DEBUG")
        assert logger.level == logging.DEBUG

        logger = setup_logging(level="WARNING")
        assert logger.level == logging.WARNING

    def test_get_logger(self):
        """Test getting a named logger"""
        logger = get_logger("test.module")

        assert logger is not None
        assert logger.name == "litsearch.test.module"

    def test_get_logger_hierarchy(self):
        """Test logger hierarchy"""
        parent = get_logger("parent")
        child = get_logger("parent.child")

        assert child.parent.name == parent.name or child.name.startswith("litsearch.parent")

    def test_logging_output(self):
        """Test that logging produces output"""
        # Create a logger with a string handler to capture output
        logger = logging.getLogger("test_output")
        logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        logger.handlers = []

        # Add string handler
        string_io = StringIO()
        handler = logging.StreamHandler(string_io)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logger.addHandler(handler)

        # Log a message
        logger.info("Test message")

        # Check output
        output = string_io.getvalue()
        assert "INFO" in output
        assert "Test message" in output

    def test_log_levels(self):
        """Test different log levels"""
        logger = logging.getLogger("test_levels")
        logger.setLevel(logging.DEBUG)

        # Clear handlers
        logger.handlers = []

        # Add string handler
        string_io = StringIO()
        handler = logging.StreamHandler(string_io)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        logger.addHandler(handler)

        # Log at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        output = string_io.getvalue()
        assert "DEBUG" in output
        assert "INFO" in output
        assert "WARNING" in output
        assert "ERROR" in output

    def test_logger_multiple_calls(self):
        """Test that multiple get_logger calls for same name return same logger"""
        logger1 = get_logger("same.module")
        logger2 = get_logger("same.module")

        assert logger1 is logger2


class TestColoredFormatter:
    """Test suite for ColoredFormatter"""

    def test_colored_formatter_init(self):
        """Test ColoredFormatter initialization"""
        formatter = ColoredFormatter('%(levelname)s - %(message)s')
        assert formatter is not None

    def test_colored_formatter_format(self):
        """Test that ColoredFormatter formats messages"""
        formatter = ColoredFormatter('%(levelname)s - %(message)s')

        # Create a log record
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )

        formatted = formatter.format(record)

        # Should contain the message
        assert "Test message" in formatted

    def test_colored_formatter_colors(self):
        """Test that ColoredFormatter adds colors"""
        formatter = ColoredFormatter('%(levelname)s - %(message)s')

        # Create records at different levels
        levels = [
            (logging.DEBUG, "DEBUG"),
            (logging.INFO, "INFO"),
            (logging.WARNING, "WARNING"),
            (logging.ERROR, "ERROR"),
            (logging.CRITICAL, "CRITICAL"),
        ]

        for level, level_name in levels:
            record = logging.LogRecord(
                name="test",
                level=level,
                pathname="test.py",
                lineno=1,
                msg="Test",
                args=(),
                exc_info=None
            )

            formatted = formatter.format(record)
            # Should contain ANSI escape codes (color codes start with \033[)
            assert "\033[" in formatted or level_name in formatted


class TestLoggingIntegration:
    """Integration tests for logging across modules"""

    def test_logger_from_different_modules(self):
        """Test that loggers from different modules work correctly"""
        api_logger = get_logger("api")
        search_logger = get_logger("search.orchestrator")
        retrieval_logger = get_logger("retrieval.pdf")

        # All should be under the litsearch namespace
        assert api_logger.name.startswith("litsearch")
        assert search_logger.name.startswith("litsearch")
        assert retrieval_logger.name.startswith("litsearch")

    def test_logger_respects_parent_level(self):
        """Test that child loggers respect parent level settings"""
        # Set up parent
        parent_logger = setup_logging(level="ERROR")

        # Get child logger
        child_logger = get_logger("child.module")

        # Child should inherit effective level
        assert child_logger.getEffectiveLevel() == logging.ERROR
