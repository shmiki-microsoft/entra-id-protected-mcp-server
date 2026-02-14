"""Unit tests for tools package initialization."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from fastmcp import FastMCP

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestToolsPackage(unittest.TestCase):
    """Tests for tools package initialization."""

    @patch("tools.pkgutil.iter_modules")
    @patch("tools.importlib.import_module")
    def test_register_all_tools(self, mock_import_module, mock_iter_modules):
        """Test register_all_tools discovers and registers tools from submodules."""
        from tools import register_all_tools

        # Mock module discovery
        mock_module_info1 = MagicMock()
        mock_module_info1.name = "userinfo"

        mock_module_info2 = MagicMock()
        mock_module_info2.name = "role_based_info"

        mock_iter_modules.return_value = [mock_module_info1, mock_module_info2]

        # Mock modules with register_tools
        mock_userinfo_module = MagicMock()
        mock_userinfo_module.register_tools = MagicMock()

        mock_role_module = MagicMock()
        mock_role_module.register_tools = MagicMock()

        def import_side_effect(module_name):
            if "userinfo" in module_name:
                return mock_userinfo_module
            elif "role_based_info" in module_name:
                return mock_role_module
            return MagicMock()

        mock_import_module.side_effect = import_side_effect

        # Test registration
        mcp = FastMCP("test-server")
        register_all_tools(mcp)

        # Verify register_tools was called
        mock_userinfo_module.register_tools.assert_called_once_with(mcp)
        mock_role_module.register_tools.assert_called_once_with(mcp)

    @patch("tools.pkgutil.iter_modules")
    @patch("tools.importlib.import_module")
    def test_register_all_tools_skips_modules_without_register(
        self, mock_import_module, mock_iter_modules
    ):
        """Test register_all_tools skips modules without register_tools function."""
        from tools import register_all_tools

        # Mock module discovery
        mock_module_info = MagicMock()
        mock_module_info.name = "some_helper"
        mock_iter_modules.return_value = [mock_module_info]

        # Mock module without register_tools
        mock_helper_module = MagicMock()
        del mock_helper_module.register_tools  # Remove register_tools attribute
        mock_import_module.return_value = mock_helper_module

        # Test registration (should not raise)
        mcp = FastMCP("test-server")
        register_all_tools(mcp)  # Should complete without error


if __name__ == "__main__":
    unittest.main()
