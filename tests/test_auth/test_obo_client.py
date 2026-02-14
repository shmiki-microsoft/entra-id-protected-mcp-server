"""Unit tests for auth.obo_client module."""

import os
import sys
import time
import unittest
from unittest.mock import MagicMock, patch

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from auth.obo_client import OboSettings, OnBehalfOfCredential


class TestOboSettings(unittest.TestCase):
    """Tests for OboSettings dataclass."""

    def test_obo_settings_creation(self):
        """Test OboSettings can be created with required fields."""
        settings = OboSettings(
            tenant_id="test-tenant-id",
            client_id="test-client-id",
            client_secret="test-secret",
            scope="https://management.azure.com/.default",
        )
        self.assertEqual(settings.tenant_id, "test-tenant-id")
        self.assertEqual(settings.client_id, "test-client-id")
        self.assertEqual(settings.client_secret, "test-secret")
        self.assertEqual(settings.scope, "https://management.azure.com/.default")


class TestOnBehalfOfCredential(unittest.TestCase):
    """Tests for OnBehalfOfCredential class."""

    def setUp(self):
        """Set up test fixtures."""
        self.settings = OboSettings(
            tenant_id="test-tenant-id",
            client_id="test-client-id",
            client_secret="test-secret",
            scope="https://management.azure.com/.default",
        )
        self.user_assertion = "test-user-token"

    def test_credential_initialization(self):
        """Test OnBehalfOfCredential initializes correctly."""
        credential = OnBehalfOfCredential(self.settings, self.user_assertion)
        self.assertEqual(credential._settings, self.settings)
        self.assertEqual(credential._user_assertion, self.user_assertion)

    @patch("auth.obo_client.msal.ConfidentialClientApplication")
    def test_get_token_success(self, mock_msal_app):
        """Test get_token successfully acquires OBO token."""
        # Mock MSAL response
        mock_app_instance = MagicMock()
        current_time = int(time.time())
        mock_app_instance.acquire_token_on_behalf_of.return_value = {
            "access_token": "test-obo-token",
            "expires_in": 3600,
        }
        mock_msal_app.return_value = mock_app_instance

        credential = OnBehalfOfCredential(self.settings, self.user_assertion)
        access_token = credential.get_token()

        # Verify MSAL was called correctly
        mock_msal_app.assert_called_once_with(
            client_id="test-client-id",
            client_credential="test-secret",
            authority="https://login.microsoftonline.com/test-tenant-id",
        )
        mock_app_instance.acquire_token_on_behalf_of.assert_called_once_with(
            user_assertion="test-user-token",
            scopes=["https://management.azure.com/.default"],
        )

        # Verify access token
        self.assertEqual(access_token.token, "test-obo-token")
        self.assertGreaterEqual(access_token.expires_on, current_time + 3500)

    @patch("auth.obo_client.msal.ConfidentialClientApplication")
    def test_get_token_failure(self, mock_msal_app):
        """Test get_token raises RuntimeError on failure."""
        # Mock MSAL error response
        mock_app_instance = MagicMock()
        mock_app_instance.acquire_token_on_behalf_of.return_value = {
            "error": "invalid_grant",
            "error_description": "AADSTS50013: Assertion failed signature validation.",
        }
        mock_msal_app.return_value = mock_app_instance

        credential = OnBehalfOfCredential(self.settings, self.user_assertion)

        with self.assertRaises(RuntimeError) as context:
            credential.get_token()

        self.assertIn("obo_token_acquisition_failed", str(context.exception))

    @patch("auth.obo_client.msal.ConfidentialClientApplication")
    def test_get_token_custom_expires_in(self, mock_msal_app):
        """Test get_token handles custom expires_in value."""
        mock_app_instance = MagicMock()
        current_time = int(time.time())
        mock_app_instance.acquire_token_on_behalf_of.return_value = {
            "access_token": "test-obo-token",
            "expires_in": 7200,  # 2 hours
        }
        mock_msal_app.return_value = mock_app_instance

        credential = OnBehalfOfCredential(self.settings, self.user_assertion)
        access_token = credential.get_token()

        self.assertGreaterEqual(access_token.expires_on, current_time + 7100)

    @patch("auth.obo_client.msal.ConfidentialClientApplication")
    def test_get_token_default_expires_in(self, mock_msal_app):
        """Test get_token uses default expires_in when not provided."""
        mock_app_instance = MagicMock()
        current_time = int(time.time())
        mock_app_instance.acquire_token_on_behalf_of.return_value = {
            "access_token": "test-obo-token",
            # No expires_in field
        }
        mock_msal_app.return_value = mock_app_instance

        credential = OnBehalfOfCredential(self.settings, self.user_assertion)
        access_token = credential.get_token()

        # Should use default of 3599 seconds
        self.assertGreaterEqual(access_token.expires_on, current_time + 3500)


if __name__ == "__main__":
    unittest.main()
