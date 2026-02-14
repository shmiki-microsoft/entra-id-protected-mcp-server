"""Unit tests for common.logging_config module."""

import logging
import os
import sys
import unittest

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from common.logging_config import LoggerConfig


class TestLoggerConfig(unittest.TestCase):
    """Tests for LoggerConfig class."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset logging configuration before each test
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.root.setLevel(logging.WARNING)

    def test_logger_config_default_values(self):
        """Test LoggerConfig with default values."""
        config = LoggerConfig()
        self.assertEqual(config.app_log_level, "INFO")
        self.assertEqual(config.auth_log_level, "INFO")
        self.assertEqual(config.mcp_server_log_level, "INFO")
        self.assertIn("%(asctime)s", config.format_string)
        self.assertIn("%(levelname)s", config.format_string)

    def test_logger_config_custom_values(self):
        """Test LoggerConfig with custom values."""
        config = LoggerConfig(
            app_log_level="DEBUG",
            auth_log_level="WARNING",
            mcp_server_log_level="ERROR",
        )
        self.assertEqual(config.app_log_level, "DEBUG")
        self.assertEqual(config.auth_log_level, "WARNING")
        self.assertEqual(config.mcp_server_log_level, "ERROR")

    def test_logger_config_auth_defaults_to_app(self):
        """Test that auth_log_level defaults to app_log_level when not specified."""
        config = LoggerConfig(app_log_level="DEBUG")
        self.assertEqual(config.auth_log_level, "DEBUG")

    def test_logger_config_mcp_defaults_to_app(self):
        """Test that mcp_server_log_level defaults to app_log_level when not specified."""
        config = LoggerConfig(app_log_level="WARNING")
        self.assertEqual(config.mcp_server_log_level, "WARNING")

    def test_logger_config_case_normalization(self):
        """Test that log levels are normalized to uppercase."""
        config = LoggerConfig(
            app_log_level="debug",
            auth_log_level="warning",
            mcp_server_log_level="error",
        )
        self.assertEqual(config.app_log_level, "DEBUG")
        self.assertEqual(config.auth_log_level, "WARNING")
        self.assertEqual(config.mcp_server_log_level, "ERROR")

    def test_logger_config_configure(self):
        """Test that configure() sets up logging without errors."""
        config = LoggerConfig(app_log_level="DEBUG")
        config.configure()  # Should not raise any exceptions

        # Verify root logger has been configured
        self.assertTrue(len(logging.root.handlers) > 0)

    def test_logger_config_get_app_logger(self):
        """Test get_app_logger method."""
        config = LoggerConfig(app_log_level="DEBUG")
        logger = config.get_app_logger("test.app")
        self.assertEqual(logger.level, logging.DEBUG)

    def test_logger_config_get_auth_logger(self):
        """Test get_auth_logger method."""
        config = LoggerConfig(auth_log_level="WARNING")
        logger = config.get_auth_logger("test.auth")
        self.assertEqual(logger.level, logging.WARNING)

    def test_logger_config_get_mcp_server_logger(self):
        """Test get_mcp_server_logger method."""
        config = LoggerConfig(mcp_server_log_level="ERROR")
        logger = config.get_mcp_server_logger("test.mcp")
        self.assertEqual(logger.level, logging.ERROR)

    def test_logger_config_str_representation(self):
        """Test string representation of LoggerConfig."""
        config = LoggerConfig(
            app_log_level="DEBUG", auth_log_level="INFO", mcp_server_log_level="WARNING"
        )
        str_repr = str(config)
        self.assertIn("DEBUG", str_repr)
        self.assertIn("INFO", str_repr)
        self.assertIn("WARNING", str_repr)

    def test_logger_config_custom_format(self):
        """Test LoggerConfig with custom format string."""
        custom_format = "%(name)s - %(message)s"
        config = LoggerConfig(format_string=custom_format)
        self.assertEqual(config.format_string, custom_format)


if __name__ == "__main__":
    unittest.main()
