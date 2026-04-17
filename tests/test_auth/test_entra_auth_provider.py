"""Unit tests for auth.entra_auth_provider module."""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import requests

# Add src to path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from starlette.authentication import AuthenticationError

from auth.entra_auth_provider import EntraIDAuthProvider, build_obo_credential


class TestEntraIDAuthProvider(unittest.IsolatedAsyncioTestCase):
    """Tests for EntraIDAuthProvider class."""

    def setUp(self):
        """Set up test fixtures."""
        self.tenant_id = "test-tenant-id"
        self.audience = "test-audience"
        self.required_scopes = ["user.read", "files.read"]
        self.required_roles = ["access_as_application"]

    @patch("auth.entra_auth_provider.requests.get")
    def test_provider_initialization_success(self, mock_get):
        """Test EntraIDAuthProvider initializes successfully."""
        # Mock JWKS response
        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": [{"kid": "test-key-id"}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        provider = EntraIDAuthProvider(
            tenant_id=self.tenant_id,
            audience=self.audience,
            required_scopes=self.required_scopes,
            required_roles=self.required_roles,
        )

        self.assertEqual(provider.tenant_id, self.tenant_id)
        self.assertEqual(provider.audience, self.audience)
        self.assertEqual(provider.required_scopes, [])
        self.assertEqual(provider.custom_required_scopes, self.required_scopes)
        self.assertEqual(provider.required_roles, self.required_roles)
        self.assertEqual(
            provider.issuer, f"https://login.microsoftonline.com/{self.tenant_id}/v2.0"
        )
        self.assertEqual(
            provider.jwks_url,
            f"https://login.microsoftonline.com/{self.tenant_id}/discovery/v2.0/keys",
        )

    @patch("auth.entra_auth_provider.requests.get")
    def test_provider_initialization_jwks_fetch_failure(self, mock_get):
        """Test EntraIDAuthProvider raises error when JWKS fetch fails."""
        mock_get.side_effect = requests.RequestException("Network error")

        with self.assertRaises(ValueError) as context:
            EntraIDAuthProvider(
                tenant_id=self.tenant_id,
                audience=self.audience,
            )

        self.assertIn("jwks_fetch_failed", str(context.exception))

    @patch("auth.entra_auth_provider.logger.info")
    @patch("auth.entra_auth_provider.jwt.decode")
    @patch("auth.entra_auth_provider.requests.get")
    async def test_verify_token_success(
        self, mock_get, mock_jwt_decode, mock_logger_info
    ):
        """Test verify_token successfully validates a token."""
        # Mock JWKS response
        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": [{"kid": "test-key-id"}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock JWT decode
        mock_jwt_decode.return_value = {
            "sub": "test-user-id",
            "scp": "user.read files.read",
            "azp": "test-client-id",
            "aud": "test-audience",
            "iss": f"https://login.microsoftonline.com/{self.tenant_id}/v2.0",
        }

        provider = EntraIDAuthProvider(
            tenant_id=self.tenant_id,
            audience=self.audience,
            required_scopes=self.required_scopes,
        )

        access_token = await provider.verify_token("test-jwt-token")

        self.assertEqual(access_token.token, "test-jwt-token")
        self.assertEqual(access_token.scopes, ["user.read", "files.read"])
        self.assertEqual(access_token.client_id, "test-client-id")
        mock_logger_info.assert_any_call(
            "Token validation succeeded via scopes: %s",
            "files.read, user.read",
        )

    @patch("auth.entra_auth_provider.logger.info")
    @patch("auth.entra_auth_provider.jwt.decode")
    @patch("auth.entra_auth_provider.requests.get")
    async def test_verify_token_success_with_required_role(
        self, mock_get, mock_jwt_decode, mock_logger_info
    ):
        """Test verify_token succeeds when the required app role is present."""
        # Mock JWKS response
        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": [{"kid": "test-key-id"}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock JWT decode - scope is incomplete, but role is present
        mock_jwt_decode.return_value = {
            "sub": "test-app-id",
            "scp": "user.read",
            "roles": ["access_as_application"],
            "azp": "test-client-id",
        }

        provider = EntraIDAuthProvider(
            tenant_id=self.tenant_id,
            audience=self.audience,
            required_scopes=self.required_scopes,
            required_roles=self.required_roles,
        )

        access_token = await provider.verify_token("test-jwt-token")

        self.assertEqual(access_token.token, "test-jwt-token")
        self.assertEqual(access_token.client_id, "test-client-id")
        mock_logger_info.assert_any_call(
            "Token validation succeeded via roles: %s",
            "access_as_application",
        )

    @patch("auth.entra_auth_provider.jwt.decode")
    @patch("auth.entra_auth_provider.requests.get")
    async def test_verify_token_missing_required_permissions(
        self, mock_get, mock_jwt_decode
    ):
        """Test verify_token raises error when neither required scopes nor roles are present."""
        # Mock JWKS response
        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": [{"kid": "test-key-id"}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock JWT decode - neither required scopes nor required roles are satisfied
        mock_jwt_decode.return_value = {
            "sub": "test-user-id",
            "scp": "user.read",
            "roles": ["some_other_role"],
            "azp": "test-client-id",
        }

        provider = EntraIDAuthProvider(
            tenant_id=self.tenant_id,
            audience=self.audience,
            required_scopes=self.required_scopes,
            required_roles=self.required_roles,
        )

        with self.assertRaises(AuthenticationError) as context:
            await provider.verify_token("test-jwt-token")

        self.assertIn("missing_required_permissions", str(context.exception))

    @patch("auth.entra_auth_provider.jwt.decode")
    @patch("auth.entra_auth_provider.requests.get")
    async def test_verify_token_expired(self, mock_get, mock_jwt_decode):
        """Test verify_token raises error for expired token."""
        # Mock JWKS response
        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": [{"kid": "test-key-id"}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock JWT decode to raise JWTError with expiration message
        from jose import JWTError

        mock_jwt_decode.side_effect = JWTError("Token has expired")

        provider = EntraIDAuthProvider(
            tenant_id=self.tenant_id,
            audience=self.audience,
        )

        with self.assertRaises(AuthenticationError) as context:
            await provider.verify_token("test-jwt-token")

        self.assertIn("access_token_expired", str(context.exception))

    @patch("auth.entra_auth_provider.jwt.decode")
    @patch("auth.entra_auth_provider.requests.get")
    async def test_verify_token_invalid_issuer(self, mock_get, mock_jwt_decode):
        """Test verify_token raises error for invalid issuer."""
        # Mock JWKS response
        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": [{"kid": "test-key-id"}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock JWT decode to raise JWTError with issuer message
        from jose import JWTError

        mock_jwt_decode.side_effect = JWTError("Invalid issuer")

        provider = EntraIDAuthProvider(
            tenant_id=self.tenant_id,
            audience=self.audience,
        )

        with self.assertRaises(AuthenticationError) as context:
            await provider.verify_token("test-jwt-token")

        self.assertIn("invalid_issuer", str(context.exception))

    @patch("auth.entra_auth_provider.jwt.decode")
    @patch("auth.entra_auth_provider.requests.get")
    async def test_verify_token_invalid_audience(self, mock_get, mock_jwt_decode):
        """Test verify_token raises error for invalid audience."""
        # Mock JWKS response
        mock_response = MagicMock()
        mock_response.json.return_value = {"keys": [{"kid": "test-key-id"}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock JWT decode to raise JWTError with audience message
        from jose import JWTError

        mock_jwt_decode.side_effect = JWTError("Invalid audience")

        provider = EntraIDAuthProvider(
            tenant_id=self.tenant_id,
            audience=self.audience,
        )

        with self.assertRaises(AuthenticationError) as context:
            await provider.verify_token("test-jwt-token")

        self.assertIn("invalid_audience", str(context.exception))


class TestBuildOboCredential(unittest.TestCase):
    """Tests for build_obo_credential function."""

    @patch("auth.entra_auth_provider.Settings")
    @patch("auth.entra_auth_provider.OnBehalfOfCredential")
    def test_build_obo_credential_success(self, mock_obo_credential, mock_settings):
        """Test build_obo_credential creates credential successfully."""
        # Mock settings
        mock_settings_instance = MagicMock()
        mock_settings_instance.entra_tenant_id = "test-tenant-id"
        mock_settings_instance.entra_app_client_id = "test-client-id"
        mock_settings_instance.entra_app_client_secret = "test-secret"
        mock_settings.return_value = mock_settings_instance

        user_jwt = "test-user-jwt"
        scope = "https://graph.microsoft.com/.default"

        build_obo_credential(user_jwt, scope)

        # Verify OnBehalfOfCredential was called
        mock_obo_credential.assert_called_once()
        call_args = mock_obo_credential.call_args
        self.assertEqual(call_args[0][1], user_jwt)

    @patch("auth.entra_auth_provider.Settings")
    def test_build_obo_credential_missing_tenant_id(self, mock_settings):
        """Test build_obo_credential raises error when tenant_id is missing."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.entra_tenant_id = ""
        mock_settings.return_value = mock_settings_instance

        with self.assertRaises(RuntimeError) as context:
            build_obo_credential("test-jwt", "test-scope")

        self.assertIn("ENTRA_TENANT_ID", str(context.exception))

    @patch("auth.entra_auth_provider.Settings")
    def test_build_obo_credential_missing_credentials(self, mock_settings):
        """Test build_obo_credential raises error when credentials are missing."""
        mock_settings_instance = MagicMock()
        mock_settings_instance.entra_tenant_id = "test-tenant-id"
        mock_settings_instance.entra_app_client_id = ""
        mock_settings_instance.entra_app_client_secret = ""
        mock_settings.return_value = mock_settings_instance

        with self.assertRaises(RuntimeError) as context:
            build_obo_credential("test-jwt", "test-scope")

        self.assertIn("CLIENT_ID", str(context.exception))


if __name__ == "__main__":
    unittest.main()
