"""Unit tests for tools.userinfo module."""

import asyncio
import os
import sys
import unittest
from unittest.mock import patch

from fastmcp import FastMCP

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestUserInfoTools(unittest.TestCase):
    """Tests for userinfo tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.mcp = FastMCP("test-server")

        # Import after creating mcp instance
        from tools import userinfo

        userinfo.register_tools(self.mcp)

    @patch("tools.userinfo.get_user_context")
    def test_get_user_info_success(self, mock_get_user_context):
        """Test get_user_info returns raw access-token claims only."""
        mock_claims = {
            "aud": "api://test-audience",
            "sub": "test-user-id",
            "tid": "test-tenant-id",
            "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
            "roles": ["Admin", "User"],
            "amr": ["pwd", "mfa"],
            "xms_ftd": "test-ftd-claim",
        }
        mock_get_user_context.return_value = (
            ["Admin", "User"],
            "test-user-id",
            "test-client-id",
            ["user.read", "files.read"],
            mock_claims,
        )

        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("get_user_info", tool_names)

        result = asyncio.run(self.mcp._tool_manager.call_tool("get_user_info", {}))
        payload = result.structured_content

        self.assertEqual(payload, mock_claims)
        self.assertNotIn("client_id", payload)
        self.assertNotIn("subject", payload)
        self.assertNotIn("all_claims", payload)

    def test_tool_registered(self):
        """Test that get_user_info tool is registered."""
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("get_user_info", tool_names)


if __name__ == "__main__":
    unittest.main()
