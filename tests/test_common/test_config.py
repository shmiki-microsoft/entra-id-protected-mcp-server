"""Unit tests for common.config module."""

import os
import sys
import unittest
from unittest.mock import patch

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestSettings(unittest.TestCase):
    """Tests for Settings configuration class."""

    def test_settings_default_values(self):
        """Test Settings with default values when no environment variables are set."""
        env_vars_to_remove = [
            "ENTRA_TENANT_ID",
            "ENTRA_APP_CLIENT_ID",
            "ENTRA_REQUIRED_SCOPES",
            "ENTRA_APP_CLIENT_SECRET",
            "APP_LOG_LEVEL",
            "AUTH_LOG_LEVEL",
            "MCP_SERVER_LOG_LEVEL",
            "MCP_TRANSPORT",
            "MCP_HOST",
            "MCP_PORT",
            "AZURE_OBO_SCOPE",
        ]
        with patch.dict(os.environ, {}, clear=False):
            for key in env_vars_to_remove:
                os.environ.pop(key, None)
            # Need to reimport to get fresh Settings with updated env vars
            import importlib

            from common import config

            importlib.reload(config)
            from common.config import Settings

            settings = Settings()
            self.assertEqual(settings.entra_tenant_id, "")
            self.assertEqual(settings.entra_app_client_id, "")
            self.assertEqual(settings.entra_required_scopes_raw, "")
            self.assertEqual(settings.app_log_level, "INFO")
            self.assertEqual(settings.auth_log_level, "")
            self.assertEqual(settings.mcp_server_log_level, "")
            self.assertEqual(settings.mcp_transport, "streamable-http")
            self.assertEqual(settings.mcp_host, "localhost")
            self.assertEqual(settings.mcp_port, 8000)
            self.assertEqual(settings.entra_app_client_secret, "")
            self.assertEqual(
                settings.azure_obo_scope, "https://management.azure.com/.default"
            )

    def test_settings_with_environment_variables(self):
        """Test Settings with custom environment variables."""
        env = {
            "ENTRA_TENANT_ID": "test-tenant-id",
            "ENTRA_APP_CLIENT_ID": "test-client-id",
            "ENTRA_REQUIRED_SCOPES": "user.read,files.read",
            "APP_LOG_LEVEL": "DEBUG",
            "AUTH_LOG_LEVEL": "WARNING",
            "MCP_SERVER_LOG_LEVEL": "ERROR",
            "MCP_TRANSPORT": "sse",
            "MCP_HOST": "0.0.0.0",
            "MCP_PORT": "9000",
            "ENTRA_APP_CLIENT_SECRET": "test-secret",
            "AZURE_OBO_SCOPE": "https://graph.microsoft.com/.default",
        }
        with patch.dict(os.environ, env, clear=False):
            # Need to reimport to get fresh Settings with updated env vars
            import importlib

            from common import config

            importlib.reload(config)
            from common.config import Settings

            settings = Settings()
            self.assertEqual(settings.entra_tenant_id, "test-tenant-id")
            self.assertEqual(settings.entra_app_client_id, "test-client-id")
            self.assertEqual(settings.entra_required_scopes_raw, "user.read,files.read")
            self.assertEqual(settings.app_log_level, "DEBUG")
            self.assertEqual(settings.auth_log_level, "WARNING")
            self.assertEqual(settings.mcp_server_log_level, "ERROR")
            self.assertEqual(settings.mcp_transport, "sse")
            self.assertEqual(settings.mcp_host, "0.0.0.0")
            self.assertEqual(settings.mcp_port, 9000)
            self.assertEqual(settings.entra_app_client_secret, "test-secret")
            self.assertEqual(
                settings.azure_obo_scope, "https://graph.microsoft.com/.default"
            )

    def test_settings_mcp_port_conversion(self):
        """Test that MCP_PORT is correctly converted to integer."""
        with patch.dict(os.environ, {"MCP_PORT": "3000"}, clear=False):
            # Need to reimport to get fresh Settings with updated env vars
            import importlib

            from common import config

            importlib.reload(config)
            from common.config import Settings

            settings = Settings()
            self.assertEqual(settings.mcp_port, 3000)
            self.assertIsInstance(settings.mcp_port, int)


if __name__ == "__main__":
    unittest.main()
