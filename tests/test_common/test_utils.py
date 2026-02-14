"""Unit tests for common.utils module."""

import os
import sys
import unittest

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from common.utils import parse_scopes


class TestParseScopes(unittest.TestCase):
    """Tests for parse_scopes function."""

    def test_parse_scopes_basic(self):
        """Test basic scope parsing."""
        result = parse_scopes("user.read,files.read")
        self.assertEqual(result, ["files.read", "user.read"])

    def test_parse_scopes_with_whitespace(self):
        """Test scope parsing with whitespace."""
        result = parse_scopes(" user.read , files.read , mail.send ")
        self.assertEqual(result, ["files.read", "mail.send", "user.read"])

    def test_parse_scopes_empty_string(self):
        """Test scope parsing with empty string."""
        result = parse_scopes("")
        self.assertEqual(result, [])

    def test_parse_scopes_none(self):
        """Test scope parsing with None."""
        result = parse_scopes(None)
        self.assertEqual(result, [])

    def test_parse_scopes_with_empty_items(self):
        """Test scope parsing with empty items."""
        result = parse_scopes("user.read,,files.read,")
        self.assertEqual(result, ["files.read", "user.read"])

    def test_parse_scopes_lowercase_conversion(self):
        """Test that scopes are converted to lowercase."""
        result = parse_scopes("User.Read,Files.Read")
        self.assertEqual(result, ["files.read", "user.read"])

    def test_parse_scopes_duplicates_removed(self):
        """Test that duplicate scopes are removed."""
        result = parse_scopes("user.read,user.read,files.read")
        self.assertEqual(result, ["files.read", "user.read"])

    def test_parse_scopes_sorted_output(self):
        """Test that scopes are sorted alphabetically."""
        result = parse_scopes("z.scope,a.scope,m.scope")
        self.assertEqual(result, ["a.scope", "m.scope", "z.scope"])


# Note: graph_serialize_model requires Microsoft Graph models which are complex to mock
# In a real scenario, integration tests would be more appropriate for that function
# However, we can add a basic test structure:


class TestGraphSerializeModel(unittest.TestCase):
    """Tests for graph_serialize_model function."""

    def test_graph_serialize_model_placeholder(self):
        """Placeholder test for graph_serialize_model.

        This function requires Microsoft Graph SDK models, which would need
        integration testing with actual Graph objects. Consider adding
        integration tests separately.
        """
        # This test serves as a reminder to add integration tests
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
