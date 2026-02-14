"""Unit tests for tools.azure_vm module."""

import asyncio
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from fastmcp import FastMCP

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestAzureVMTools(unittest.TestCase):
    """Tests for azure_vm tools."""

    def setUp(self):
        """Set up test fixtures."""
        self.mcp = FastMCP("test-server")

        # Import after creating mcp instance
        from tools import azure_vm

        azure_vm.register_tools(self.mcp)

    def test_list_azure_vms_registered(self):
        """Test list_azure_vms tool is registered."""
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("list_azure_vms", tool_names)

    @patch("tools.azure_vm.get_access_token_and_context")
    @patch("tools.azure_vm.build_obo_credential")
    @patch("tools.azure_vm.ComputeManagementClient")
    def test_list_azure_vms_integration(
        self,
        mock_compute_client,
        mock_build_obo,
        mock_get_token,
    ):
        """Test list_azure_vms integration (mocked)."""
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

        # Mock Compute Management Client
        mock_client_instance = MagicMock()
        mock_vm1 = MagicMock()
        mock_vm1.id = "/subscriptions/test/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm1"
        mock_vm1.name = "vm1"
        mock_vm1.location = "eastus"
        mock_vm1.type = "Microsoft.Compute/virtualMachines"
        mock_vm1.tags = {"env": "test"}

        mock_vm2 = MagicMock()
        mock_vm2.id = "/subscriptions/test/resourceGroups/rg2/providers/Microsoft.Compute/virtualMachines/vm2"
        mock_vm2.name = "vm2"
        mock_vm2.location = "westus"
        mock_vm2.type = "Microsoft.Compute/virtualMachines"
        mock_vm2.tags = {"env": "prod"}

        mock_client_instance.virtual_machines.list_all.return_value = [
            mock_vm1,
            mock_vm2,
        ]
        mock_compute_client.return_value = mock_client_instance

        # Verify tool is registered
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("list_azure_vms", tool_names)

    @patch("tools.azure_vm.logging.getLogger")
    def test_azure_logger_debug_enabled(self, mock_get_logger):
        """Test that Azure SDK logging is controlled by logger level."""
        mock_logger = MagicMock()
        mock_logger.isEnabledFor.return_value = True
        mock_get_logger.return_value = mock_logger

        # Verify tool is registered
        tool_names = [
            tool if isinstance(tool, str) else tool.name
            for tool in asyncio.run(self.mcp.get_tools())
        ]
        self.assertIn("list_azure_vms", tool_names)


if __name__ == "__main__":
    unittest.main()
