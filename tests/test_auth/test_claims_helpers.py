"""Unit tests for auth.claims_helpers module."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from auth.claims_helpers import get_access_token_and_context, get_user_context, has_role


class TestClaimsHelpers(unittest.TestCase):
    """Tests for claims_helpers functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_access_token = MagicMock()
        self.mock_access_token.claims = {
            "roles": ["Admin", "User"],
            "sub": "test-user-id",
            "oid": "test-object-id",
            "upn": "testuser@example.com",
            "name": "Test User",
            "tid": "test-tenant-id",
            "scp": "user.read files.read",
        }
        self.mock_access_token.client_id = "test-client-id"
        self.mock_access_token.scopes = ["user.read", "files.read"]

    @patch("auth.claims_helpers.get_access_token")
    def test_get_user_context(self, mock_get_token):
        """Test get_user_context returns user information correctly."""
        mock_get_token.return_value = self.mock_access_token

        roles, user_id, client_id, scopes, claims = get_user_context()

        self.assertEqual(roles, ["Admin", "User"])
        self.assertEqual(user_id, "test-user-id")
        self.assertEqual(client_id, "test-client-id")
        self.assertEqual(scopes, ["user.read", "files.read"])
        self.assertEqual(claims["name"], "Test User")
        self.assertEqual(claims["tid"], "test-tenant-id")

    @patch("auth.claims_helpers.get_access_token")
    def test_get_user_context_no_roles(self, mock_get_token):
        """Test get_user_context when no roles are present."""
        self.mock_access_token.claims = {"sub": "test-user-id"}
        mock_get_token.return_value = self.mock_access_token

        roles, user_id, client_id, scopes, claims = get_user_context()

        self.assertEqual(roles, [])
        self.assertEqual(user_id, "test-user-id")

    @patch("auth.claims_helpers.get_access_token")
    def test_get_access_token_and_context(self, mock_get_token):
        """Test get_access_token_and_context returns token and context."""
        mock_get_token.return_value = self.mock_access_token

        access_token, roles, user_id, client_id, scopes, claims = (
            get_access_token_and_context()
        )

        self.assertEqual(access_token, self.mock_access_token)
        self.assertEqual(roles, ["Admin", "User"])
        self.assertEqual(user_id, "test-user-id")
        self.assertEqual(client_id, "test-client-id")
        self.assertEqual(scopes, ["user.read", "files.read"])
        self.assertEqual(claims["name"], "Test User")

    def test_has_role_true(self):
        """Test has_role returns True when role is present."""
        roles = ["Admin", "User", "Auditor"]
        self.assertTrue(has_role(roles, "Admin"))
        self.assertTrue(has_role(roles, "User"))
        self.assertTrue(has_role(roles, "Auditor"))

    def test_has_role_false(self):
        """Test has_role returns False when role is not present."""
        roles = ["User", "Auditor"]
        self.assertFalse(has_role(roles, "Admin"))
        self.assertFalse(has_role(roles, "SuperUser"))

    def test_has_role_empty_roles(self):
        """Test has_role returns False when roles list is empty."""
        roles = []
        self.assertFalse(has_role(roles, "Admin"))

    def test_has_role_case_sensitive(self):
        """Test that has_role is case-sensitive."""
        roles = ["Admin", "User"]
        self.assertFalse(has_role(roles, "admin"))
        self.assertFalse(has_role(roles, "ADMIN"))
        self.assertTrue(has_role(roles, "Admin"))


if __name__ == "__main__":
    unittest.main()
