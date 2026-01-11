# TSS PPM v3.0 - Keycloak Admin Service Tests
"""Tests for the Keycloak Admin API service."""

from unittest.mock import AsyncMock, patch, MagicMock
import pytest

pytestmark = pytest.mark.asyncio


class TestKeycloakAdminService:
    """Tests for the Keycloak Admin API service."""

    @pytest.fixture
    def sample_users_response(self):
        """Sample users list response from Keycloak."""
        return [
            {
                'id': 'user-1-uuid',
                'username': 'john.doe',
                'email': 'john.doe@tss.eu',
                'firstName': 'John',
                'lastName': 'Doe',
                'enabled': True,
                'attributes': {
                    'opco_id': ['opco-1'],
                    'function_title': ['Software Engineer'],
                    'tov_level': ['B'],
                    'manager_id': ['manager-uuid'],
                },
            },
            {
                'id': 'user-2-uuid',
                'username': 'jane.smith',
                'email': 'jane.smith@tss.eu',
                'firstName': 'Jane',
                'lastName': 'Smith',
                'enabled': True,
                'attributes': {
                    'opco_id': ['opco-1'],
                    'function_title': ['UX Designer'],
                    'tov_level': ['C'],
                    'manager_id': ['manager-uuid'],
                },
            },
        ]

    @pytest.fixture
    def sample_user_response(self):
        """Sample single user response from Keycloak."""
        return {
            'id': 'user-1-uuid',
            'username': 'john.doe',
            'email': 'john.doe@tss.eu',
            'firstName': 'John',
            'lastName': 'Doe',
            'enabled': True,
            'attributes': {
                'opco_id': ['opco-1'],
                'function_title': ['Software Engineer'],
                'tov_level': ['B'],
                'manager_id': ['manager-uuid'],
            },
        }

    @pytest.fixture
    def sample_token_response(self):
        """Sample token response for service account auth."""
        return {
            'access_token': 'mock-admin-token',
            'expires_in': 300,
            'token_type': 'Bearer',
        }

    @pytest.fixture
    def sample_realm_roles(self):
        """Sample realm roles response."""
        return [
            {'id': 'role-1', 'name': 'employee'},
            {'id': 'role-2', 'name': 'manager'},
            {'id': 'role-3', 'name': 'hr'},
            {'id': 'role-4', 'name': 'admin'},
        ]

    async def test_service_authenticates_with_client_credentials(self, sample_token_response):
        """Service should authenticate using client credentials grant."""
        from src.services.keycloak_admin import KeycloakAdminService

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_token_response
            mock_client.post.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()
            token = await service._get_admin_token()

            assert token == 'mock-admin-token'
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert 'token' in call_args[0][0]

    async def test_get_users_returns_list(self, sample_token_response, sample_users_response):
        """get_users should return list of users from Keycloak."""
        from src.services.keycloak_admin import KeycloakAdminService

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            # Token response
            token_response = MagicMock()
            token_response.status_code = 200
            token_response.json.return_value = sample_token_response

            # Users response
            users_response = MagicMock()
            users_response.status_code = 200
            users_response.json.return_value = sample_users_response

            mock_client.post.return_value = token_response
            mock_client.get.return_value = users_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()
            users = await service.get_users(opco_id='opco-1')

            assert len(users) == 2
            assert users[0]['email'] == 'john.doe@tss.eu'
            assert users[1]['email'] == 'jane.smith@tss.eu'

    async def test_get_user_by_id_returns_user(self, sample_token_response, sample_user_response):
        """get_user should return a single user by ID."""
        from src.services.keycloak_admin import KeycloakAdminService

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            token_response = MagicMock()
            token_response.status_code = 200
            token_response.json.return_value = sample_token_response

            user_response = MagicMock()
            user_response.status_code = 200
            user_response.json.return_value = sample_user_response

            mock_client.post.return_value = token_response
            mock_client.get.return_value = user_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()
            user = await service.get_user('user-1-uuid')

            assert user is not None
            assert user['id'] == 'user-1-uuid'
            assert user['email'] == 'john.doe@tss.eu'

    async def test_get_user_roles_returns_roles(self, sample_token_response, sample_realm_roles):
        """get_user_roles should return user's realm roles."""
        from src.services.keycloak_admin import KeycloakAdminService

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            token_response = MagicMock()
            token_response.status_code = 200
            token_response.json.return_value = sample_token_response

            roles_response = MagicMock()
            roles_response.status_code = 200
            roles_response.json.return_value = sample_realm_roles

            mock_client.post.return_value = token_response
            mock_client.get.return_value = roles_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()
            roles = await service.get_user_roles('user-1-uuid')

            assert len(roles) == 4
            role_names = [r['name'] for r in roles]
            assert 'employee' in role_names
            assert 'admin' in role_names

    async def test_assign_role_calls_keycloak_api(self, sample_token_response, sample_realm_roles):
        """assign_role should add a role to a user via Keycloak API."""
        from src.services.keycloak_admin import KeycloakAdminService

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            token_response = MagicMock()
            token_response.status_code = 200
            token_response.json.return_value = sample_token_response

            # Get available roles response
            available_roles_response = MagicMock()
            available_roles_response.status_code = 200
            available_roles_response.json.return_value = sample_realm_roles

            # Assign role response
            assign_response = MagicMock()
            assign_response.status_code = 204

            mock_client.post.side_effect = [token_response, assign_response]
            mock_client.get.return_value = available_roles_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()
            result = await service.assign_role('user-1-uuid', 'manager')

            assert result is True

    async def test_remove_role_calls_keycloak_api(self, sample_token_response, sample_realm_roles):
        """remove_role should remove a role from a user via Keycloak API."""
        from src.services.keycloak_admin import KeycloakAdminService

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            token_response = MagicMock()
            token_response.status_code = 200
            token_response.json.return_value = sample_token_response

            available_roles_response = MagicMock()
            available_roles_response.status_code = 200
            available_roles_response.json.return_value = sample_realm_roles

            remove_response = MagicMock()
            remove_response.status_code = 204

            mock_client.post.return_value = token_response
            mock_client.get.return_value = available_roles_response
            mock_client.delete.return_value = remove_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()
            result = await service.remove_role('user-1-uuid', 'manager')

            assert result is True

    async def test_disable_user_calls_keycloak_api(self, sample_token_response):
        """disable_user should set enabled=False via Keycloak API."""
        from src.services.keycloak_admin import KeycloakAdminService

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            token_response = MagicMock()
            token_response.status_code = 200
            token_response.json.return_value = sample_token_response

            update_response = MagicMock()
            update_response.status_code = 204

            mock_client.post.return_value = token_response
            mock_client.put.return_value = update_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()
            result = await service.disable_user('user-1-uuid')

            assert result is True
            # Verify PUT was called with enabled=False
            call_args = mock_client.put.call_args
            assert call_args.kwargs['json']['enabled'] is False

    async def test_enable_user_calls_keycloak_api(self, sample_token_response):
        """enable_user should set enabled=True via Keycloak API."""
        from src.services.keycloak_admin import KeycloakAdminService

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            token_response = MagicMock()
            token_response.status_code = 200
            token_response.json.return_value = sample_token_response

            update_response = MagicMock()
            update_response.status_code = 204

            mock_client.post.return_value = token_response
            mock_client.put.return_value = update_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()
            result = await service.enable_user('user-1-uuid')

            assert result is True
            # Verify PUT was called with enabled=True
            call_args = mock_client.put.call_args
            assert call_args.kwargs['json']['enabled'] is True

    async def test_update_user_manager_calls_keycloak_api(self, sample_token_response, sample_user_response):
        """update_user_manager should update manager_id attribute."""
        from src.services.keycloak_admin import KeycloakAdminService

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            token_response = MagicMock()
            token_response.status_code = 200
            token_response.json.return_value = sample_token_response

            get_user_response = MagicMock()
            get_user_response.status_code = 200
            get_user_response.json.return_value = sample_user_response

            update_response = MagicMock()
            update_response.status_code = 204

            mock_client.post.return_value = token_response
            mock_client.get.return_value = get_user_response
            mock_client.put.return_value = update_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()
            result = await service.update_user_manager('user-1-uuid', 'new-manager-uuid')

            assert result is True

    async def test_authentication_error_raises_exception(self):
        """Service should raise exception when authentication fails."""
        from src.services.keycloak_admin import KeycloakAdminService, KeycloakAdminError

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            error_response = MagicMock()
            error_response.status_code = 401
            error_response.text = 'Unauthorized'

            mock_client.post.return_value = error_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()

            with pytest.raises(KeycloakAdminError) as exc_info:
                await service._get_admin_token()

            assert 'authentication' in str(exc_info.value).lower()

    async def test_connection_error_raises_exception(self):
        """Service should raise exception when Keycloak is unavailable."""
        from src.services.keycloak_admin import KeycloakAdminService, KeycloakAdminError
        import httpx

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.side_effect = httpx.ConnectError('Connection refused')
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()

            with pytest.raises(KeycloakAdminError) as exc_info:
                await service._get_admin_token()

            assert 'unavailable' in str(exc_info.value).lower()

    async def test_get_available_roles_returns_realm_roles(self, sample_token_response, sample_realm_roles):
        """get_available_roles should return all realm roles."""
        from src.services.keycloak_admin import KeycloakAdminService

        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()

            token_response = MagicMock()
            token_response.status_code = 200
            token_response.json.return_value = sample_token_response

            roles_response = MagicMock()
            roles_response.status_code = 200
            roles_response.json.return_value = sample_realm_roles

            mock_client.post.return_value = token_response
            mock_client.get.return_value = roles_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            service = KeycloakAdminService()
            roles = await service.get_available_roles()

            assert len(roles) == 4
            role_names = [r['name'] for r in roles]
            assert 'employee' in role_names
            assert 'manager' in role_names
            assert 'hr' in role_names
            assert 'admin' in role_names
