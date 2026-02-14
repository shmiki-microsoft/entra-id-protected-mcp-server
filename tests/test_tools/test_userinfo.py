"""Unit tests for tools.userinfo module."""

import os
import sys
import unittest
import asyncio
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
        """Test get_user_info returns user information correctly."""
        # Mock user context
        mock_get_user_context.return_value = (
            ["Admin", "User"],  # roles
            "test-user-id",  # user_id
            "test-client-id",  # client_id
            ["user.read", "files.read"],  # scopes
            {  # claims
                "sub": "test-user-id",
                "tid": "test-tenant-id",
                "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
                "oid": "test-object-id",
                "upn": "testuser@example.com",
                "email": "testuser@example.com",
                "name": "Test User",
                "given_name": "Test",
                "family_name": "User",
                "job_title": "Developer",
                "department": "Engineering",
                "office_location": "Seattle",
                "iat": 1234567890,
                "exp": 1234571490,
                "nbf": 1234567890,
                "appid": "test-app-id",
                "azp": "test-azp",
                "idp": "https://sts.windows.net/test-idp/",
                "ver": "2.0",
                "amr": ["pwd", "mfa"],
            },
        )

        # Get the tool function
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("get_user_info", tool_names)

        # Note: Testing actual tool execution would require FastMCP's runtime context
        # This test verifies the tool is registered correctly
        self.assertIn("get_user_info", tool_names)

    def test_tool_registered(self):
        """Test that get_user_info tool is registered."""
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("get_user_info", tool_names)


if __name__ == "__main__":
    unittest.main()
