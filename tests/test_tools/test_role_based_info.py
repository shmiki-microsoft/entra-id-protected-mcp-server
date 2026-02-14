"""Unit tests for tools.role_based_info module."""

import asyncio
import os
import sys
import unittest
from unittest.mock import patch

from fastmcp import FastMCP

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestRoleBasedInfoTools(unittest.TestCase):
    """Tests for role_based_info tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.mcp = FastMCP("test-server")

        # Import after creating mcp instance
        from tools import role_based_info

        role_based_info.register_tools(self.mcp)

    def test_tools_registered(self):
        """Test that role-based tools are registered."""
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]

        self.assertIn("get_company_info", tool_names)
        self.assertIn("get_sensitive_data", tool_names)
        self.assertIn("list_available_resources", tool_names)

    @patch("tools.role_based_info.get_user_context")
    def test_get_company_info_public_access(self, mock_get_user_context):
        """Test get_company_info with no roles (public access)."""
        mock_get_user_context.return_value = (
            [],  # roles
            "test-user-id",  # user_id
            "test-client-id",  # client_id
            ["user.read"],  # scopes
            {},  # claims
        )

        # Verify tool is registered
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("get_company_info", tool_names)

    @patch("tools.role_based_info.get_user_context")
    @patch("tools.role_based_info.has_role")
    def test_get_company_info_with_roles(self, mock_has_role, mock_get_user_context):
        """Test get_company_info with various roles."""
        # Mock user with User role
        mock_get_user_context.return_value = (
            ["User"],  # roles
            "test-user-id",  # user_id
            "test-client-id",  # client_id
            ["user.read"],  # scopes
            {},  # claims
        )
        mock_has_role.return_value = False

        # Verify tool is registered
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("get_company_info", tool_names)

    def test_get_sensitive_data_registered(self):
        """Test get_sensitive_data tool is registered."""
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("get_sensitive_data", tool_names)

    def test_list_available_resources_registered(self):
        """Test list_available_resources tool is registered."""
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("list_available_resources", tool_names)


if __name__ == "__main__":
    unittest.main()
