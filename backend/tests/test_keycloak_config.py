# TSS PPM v3.0 - Keycloak Configuration Tests
"""Integration tests for Keycloak hostname configuration.

These tests verify that Keycloak is properly configured with v2 hostname settings
and returns correct URLs in the OpenID Connect discovery document.
"""

import os

import httpx
import pytest

# Expected configuration from environment
KEYCLOAK_URL = os.getenv('KEYCLOAK_ISSUER_URL', 'http://localhost:8080')
KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM', 'tss-ppm')

# The expected issuer URL that should appear in tokens and discovery
EXPECTED_ISSUER = f'{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}'


@pytest.fixture
def keycloak_discovery_url() -> str:
    """Return the OpenID Connect discovery endpoint URL."""
    return f'{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/.well-known/openid-configuration'


class TestKeycloakConfiguration:
    """Integration tests for Keycloak v2 hostname configuration."""

    @pytest.mark.integration
    async def test_discovery_endpoint_responds(self, keycloak_discovery_url: str):
        """Verify that the .well-known/openid-configuration endpoint responds.

        AC-4: OpenID Connect discovery endpoint returns correct URLs.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(keycloak_discovery_url, timeout=10.0)
            except httpx.ConnectError:
                pytest.skip('Keycloak is not running - skipping integration test')

            assert response.status_code == 200, (
                f'Discovery endpoint returned {response.status_code}'
            )

            data = response.json()
            assert 'issuer' in data, 'Discovery response missing issuer field'
            assert 'token_endpoint' in data, 'Discovery response missing token_endpoint'
            assert 'authorization_endpoint' in data, 'Discovery response missing authorization_endpoint'

    @pytest.mark.integration
    async def test_issuer_url_matches_expected_hostname(self, keycloak_discovery_url: str):
        """Verify that the issuer URL matches the expected hostname.

        AC-5: Token endpoint URLs in discovery document match configured hostname.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(keycloak_discovery_url, timeout=10.0)
            except httpx.ConnectError:
                pytest.skip('Keycloak is not running - skipping integration test')

            assert response.status_code == 200
            data = response.json()

            issuer = data.get('issuer')
            assert issuer == EXPECTED_ISSUER, (
                f'Issuer mismatch: expected {EXPECTED_ISSUER}, got {issuer}'
            )

    @pytest.mark.integration
    async def test_token_endpoint_url_is_correct(self, keycloak_discovery_url: str):
        """Verify that the token endpoint URL uses the correct hostname.

        AC-5: Token endpoint URLs in discovery document match configured hostname.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(keycloak_discovery_url, timeout=10.0)
            except httpx.ConnectError:
                pytest.skip('Keycloak is not running - skipping integration test')

            assert response.status_code == 200
            data = response.json()

            token_endpoint = data.get('token_endpoint')
            expected_token_endpoint = f'{EXPECTED_ISSUER}/protocol/openid-connect/token'

            assert token_endpoint == expected_token_endpoint, (
                f'Token endpoint mismatch: expected {expected_token_endpoint}, got {token_endpoint}'
            )

    @pytest.mark.integration
    async def test_authorization_endpoint_url_is_correct(self, keycloak_discovery_url: str):
        """Verify that the authorization endpoint URL uses the correct hostname."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(keycloak_discovery_url, timeout=10.0)
            except httpx.ConnectError:
                pytest.skip('Keycloak is not running - skipping integration test')

            assert response.status_code == 200
            data = response.json()

            auth_endpoint = data.get('authorization_endpoint')
            expected_auth_endpoint = f'{EXPECTED_ISSUER}/protocol/openid-connect/auth'

            assert auth_endpoint == expected_auth_endpoint, (
                f'Auth endpoint mismatch: expected {expected_auth_endpoint}, got {auth_endpoint}'
            )
