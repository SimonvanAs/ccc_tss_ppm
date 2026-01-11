# TSS PPM v3.0 - Keycloak Admin Service
"""Service for Keycloak Admin REST API operations."""

from typing import Any, Dict, List, Optional

import httpx

from src.config import settings


class KeycloakAdminError(Exception):
    """Exception raised for Keycloak Admin API errors."""
    pass


class KeycloakAdminService:
    """Service for interacting with Keycloak Admin REST API.

    Uses service account authentication (client credentials grant) to
    perform administrative operations like user management and role assignment.
    """

    def __init__(self):
        """Initialize the Keycloak Admin service."""
        self._token: Optional[str] = None

    async def _get_admin_token(self) -> str:
        """Authenticate with Keycloak using client credentials grant.

        Returns:
            The access token for admin API calls.

        Raises:
            KeycloakAdminError: If authentication fails.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    settings.keycloak_token_url,
                    data={
                        'grant_type': 'client_credentials',
                        'client_id': settings.keycloak_admin_client_id,
                        'client_secret': settings.keycloak_admin_client_secret,
                    },
                )

                if response.status_code != 200:
                    raise KeycloakAdminError(
                        f'Authentication failed: {response.text}'
                    )

                data = response.json()
                self._token = data['access_token']
                return self._token

        except httpx.ConnectError as e:
            raise KeycloakAdminError(
                f'Keycloak service unavailable: {str(e)}'
            )

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """Make an authenticated request to the Keycloak Admin API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request

        Returns:
            The HTTP response
        """
        if self._token is None:
            await self._get_admin_token()

        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self._token}'

        async with httpx.AsyncClient() as client:
            url = f'{settings.keycloak_admin_api_url}{endpoint}'
            response = await getattr(client, method.lower())(
                url,
                headers=headers,
                **kwargs
            )
            return response

    async def get_users(
        self,
        opco_id: Optional[str] = None,
        search: Optional[str] = None,
        first: int = 0,
        max_results: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get list of users from Keycloak.

        Args:
            opco_id: Filter by OpCo ID attribute
            search: Search term for username/email/name
            first: Pagination offset
            max_results: Maximum number of results

        Returns:
            List of user dictionaries
        """
        params = {
            'first': first,
            'max': max_results,
        }

        if search:
            params['search'] = search

        response = await self._request('GET', '/users', params=params)

        if response.status_code != 200:
            raise KeycloakAdminError(f'Failed to get users: {response.text}')

        users = response.json()

        # Filter by opco_id if specified
        if opco_id:
            users = [
                u for u in users
                if u.get('attributes', {}).get('opco_id', [None])[0] == opco_id
            ]

        return users

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get a single user by ID.

        Args:
            user_id: The Keycloak user ID

        Returns:
            User dictionary
        """
        response = await self._request('GET', f'/users/{user_id}')

        if response.status_code == 404:
            raise KeycloakAdminError(f'User not found: {user_id}')

        if response.status_code != 200:
            raise KeycloakAdminError(f'Failed to get user: {response.text}')

        return response.json()

    async def get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        """Get the realm roles assigned to a user.

        Args:
            user_id: The Keycloak user ID

        Returns:
            List of role dictionaries
        """
        response = await self._request(
            'GET',
            f'/users/{user_id}/role-mappings/realm'
        )

        if response.status_code != 200:
            raise KeycloakAdminError(
                f'Failed to get user roles: {response.text}'
            )

        return response.json()

    async def get_available_roles(self) -> List[Dict[str, Any]]:
        """Get all available realm roles.

        Returns:
            List of role dictionaries
        """
        response = await self._request('GET', '/roles')

        if response.status_code != 200:
            raise KeycloakAdminError(
                f'Failed to get available roles: {response.text}'
            )

        return response.json()

    async def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign a realm role to a user.

        Args:
            user_id: The Keycloak user ID
            role_name: The name of the role to assign

        Returns:
            True if successful
        """
        # Get the role by name to get its ID
        roles = await self.get_available_roles()
        role = next((r for r in roles if r['name'] == role_name), None)

        if role is None:
            raise KeycloakAdminError(f'Role not found: {role_name}')

        response = await self._request(
            'POST',
            f'/users/{user_id}/role-mappings/realm',
            json=[role]
        )

        if response.status_code not in (200, 204):
            raise KeycloakAdminError(
                f'Failed to assign role: {response.text}'
            )

        return True

    async def remove_role(self, user_id: str, role_name: str) -> bool:
        """Remove a realm role from a user.

        Args:
            user_id: The Keycloak user ID
            role_name: The name of the role to remove

        Returns:
            True if successful
        """
        # Get the role by name to get its ID
        roles = await self.get_available_roles()
        role = next((r for r in roles if r['name'] == role_name), None)

        if role is None:
            raise KeycloakAdminError(f'Role not found: {role_name}')

        response = await self._request(
            'DELETE',
            f'/users/{user_id}/role-mappings/realm',
            json=[role]
        )

        if response.status_code not in (200, 204):
            raise KeycloakAdminError(
                f'Failed to remove role: {response.text}'
            )

        return True

    async def disable_user(self, user_id: str) -> bool:
        """Disable a user account.

        Args:
            user_id: The Keycloak user ID

        Returns:
            True if successful
        """
        response = await self._request(
            'PUT',
            f'/users/{user_id}',
            json={'enabled': False}
        )

        if response.status_code not in (200, 204):
            raise KeycloakAdminError(
                f'Failed to disable user: {response.text}'
            )

        return True

    async def enable_user(self, user_id: str) -> bool:
        """Enable a user account.

        Args:
            user_id: The Keycloak user ID

        Returns:
            True if successful
        """
        response = await self._request(
            'PUT',
            f'/users/{user_id}',
            json={'enabled': True}
        )

        if response.status_code not in (200, 204):
            raise KeycloakAdminError(
                f'Failed to enable user: {response.text}'
            )

        return True

    async def update_user_manager(
        self,
        user_id: str,
        manager_id: str
    ) -> bool:
        """Update the manager_id attribute for a user.

        Args:
            user_id: The Keycloak user ID
            manager_id: The new manager's Keycloak user ID

        Returns:
            True if successful
        """
        # Get current user to preserve other attributes
        user = await self.get_user(user_id)
        attributes = user.get('attributes', {})
        attributes['manager_id'] = [manager_id]

        response = await self._request(
            'PUT',
            f'/users/{user_id}',
            json={'attributes': attributes}
        )

        if response.status_code not in (200, 204):
            raise KeycloakAdminError(
                f'Failed to update user manager: {response.text}'
            )

        return True
