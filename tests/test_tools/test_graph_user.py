"""Unit tests for tools.graph_user module."""

import asyncio
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastmcp import FastMCP

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestGraphUserTools(unittest.TestCase):
    """Tests for graph_user tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.mcp = FastMCP("test-server")

        # Import after creating mcp instance
        from tools import graph_user

        graph_user.register_tools(self.mcp)

    def test_tools_registered(self):
        """Test that Graph tools are registered."""
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]

        self.assertIn("get_graph_me", tool_names)
        self.assertIn("get_graph_me_with_select_query", tool_names)

    def test_get_graph_me_registered(self):
        """Test get_graph_me tool is registered."""
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("get_graph_me", tool_names)

    def test_get_graph_me_with_select_query_registered(self):
        """Test get_graph_me_with_select_query tool is registered."""
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("get_graph_me_with_select_query", tool_names)

    @patch("tools.graph_user.get_access_token_and_context")
    @patch("tools.graph_user.build_obo_credential")
    @patch("tools.graph_user.GraphServiceClient")
    def test_get_graph_me_integration(
        self, mock_graph_client, mock_build_obo, mock_get_token
    ):
        """Test get_graph_me integration (mocked)."""
        # Mock access token context
        mock_access_token = MagicMock()
        mock_access_token.token = "test-user-token"
        mock_get_token.return_value = (
            mock_access_token,
            ["User"],
            "test-user-id",
            "test-client-id",
            ["user.read"],
            {},
        )

        # Mock OBO credential
        mock_credential = MagicMock()
        mock_build_obo.return_value = mock_credential

        # Mock Graph client response
        mock_client_instance = MagicMock()
        mock_me = MagicMock()
        mock_me.get = AsyncMock(return_value=MagicMock())
        mock_client_instance.me = mock_me
        mock_graph_client.return_value = mock_client_instance

        # Verify tool is registered
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("get_graph_me", tool_names)


if __name__ == "__main__":
    unittest.main()
