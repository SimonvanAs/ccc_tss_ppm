# TSS PPM v3.0 - Admin API Tests
"""Tests for admin API endpoints."""

from unittest.mock import AsyncMock
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.routers.admin import get_keycloak_admin

pytestmark = pytest.mark.asyncio


@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    return CurrentUser(
        keycloak_id='admin-uuid',
        email='admin@tss.eu',
        name='Admin User',
        roles=['admin'],
        opco_id='opco-1',
    )


@pytest.fixture
def non_admin_user():
    """Create a non-admin user for testing."""
    return CurrentUser(
        keycloak_id='user-uuid',
        email='user@tss.eu',
        name='Regular User',
        roles=['employee'],
        opco_id='opco-1',
    )


@pytest.fixture
def sample_users():
    """Sample user data from Keycloak."""
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
def sample_roles():
    """Sample realm roles from Keycloak."""
    return [
        {'id': 'role-1', 'name': 'employee'},
        {'id': 'role-2', 'name': 'manager'},
    ]


class TestAdminUsersList:
    """Tests for GET /api/v1/admin/users endpoint."""

    async def test_list_users_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from listing users."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/users')
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_list_users_returns_users_for_admin(
        self,
        admin_user,
        sample_users,
    ):
        """Admin users should be able to list users."""
        mock_keycloak = AsyncMock()
        mock_keycloak.get_users.return_value = sample_users
        mock_keycloak.get_user_roles.return_value = []

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_keycloak_admin] = lambda: mock_keycloak

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/users')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2

        app.dependency_overrides.clear()

    async def test_list_users_with_search(
        self,
        admin_user,
        sample_users,
    ):
        """Search should filter users by name/email."""
        filtered_users = [sample_users[0]]  # Only John
        mock_keycloak = AsyncMock()
        mock_keycloak.get_users.return_value = filtered_users
        mock_keycloak.get_user_roles.return_value = []

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_keycloak_admin] = lambda: mock_keycloak

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/users?search=john')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]['email'] == 'john.doe@tss.eu'

        app.dependency_overrides.clear()


class TestAdminUserDetail:
    """Tests for GET /api/v1/admin/users/{id} endpoint."""

    async def test_get_user_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from viewing user details."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/users/user-1-uuid')
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_get_user_returns_user_for_admin(
        self,
        admin_user,
        sample_users,
        sample_roles,
    ):
        """Admin users should be able to view user details."""
        user = sample_users[0]
        mock_keycloak = AsyncMock()
        mock_keycloak.get_user.return_value = user
        mock_keycloak.get_user_roles.return_value = sample_roles

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_keycloak_admin] = lambda: mock_keycloak

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/users/user-1-uuid')
            assert response.status_code == 200
            data = response.json()
            assert data['id'] == 'user-1-uuid'
            assert data['email'] == 'john.doe@tss.eu'

        app.dependency_overrides.clear()


class TestAdminUserRoles:
    """Tests for PUT /api/v1/admin/users/{id}/roles endpoint."""

    async def test_update_roles_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from updating roles."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/users/user-1-uuid/roles',
                json={'roles': ['employee', 'manager']},
            )
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_update_roles_assigns_and_removes_roles(self, admin_user):
        """Admin should be able to update user roles."""
        mock_keycloak = AsyncMock()
        mock_keycloak.get_user_roles.return_value = [{'name': 'employee'}]
        mock_keycloak.assign_role.return_value = True
        mock_keycloak.remove_role.return_value = True

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_keycloak_admin] = lambda: mock_keycloak

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/users/user-1-uuid/roles',
                json={'roles': ['manager']},  # Remove employee, add manager
            )
            assert response.status_code == 200

        app.dependency_overrides.clear()


class TestAdminUserManager:
    """Tests for PUT /api/v1/admin/users/{id}/manager endpoint."""

    async def test_update_manager_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from updating manager."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/users/user-1-uuid/manager',
                json={'manager_id': 'new-manager-uuid'},
            )
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_update_manager_changes_manager(self, admin_user):
        """Admin should be able to update user's manager."""
        mock_keycloak = AsyncMock()
        mock_keycloak.update_user_manager.return_value = True

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_keycloak_admin] = lambda: mock_keycloak

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/users/user-1-uuid/manager',
                json={'manager_id': 'new-manager-uuid'},
            )
            assert response.status_code == 200

        app.dependency_overrides.clear()


class TestAdminUserStatus:
    """Tests for PUT /api/v1/admin/users/{id}/status endpoint."""

    async def test_update_status_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from updating status."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/users/user-1-uuid/status',
                json={'enabled': False},
            )
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_disable_user(self, admin_user):
        """Admin should be able to disable a user."""
        mock_keycloak = AsyncMock()
        mock_keycloak.disable_user.return_value = True

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_keycloak_admin] = lambda: mock_keycloak

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/users/user-1-uuid/status',
                json={'enabled': False},
            )
            assert response.status_code == 200

        app.dependency_overrides.clear()

    async def test_enable_user(self, admin_user):
        """Admin should be able to enable a user."""
        mock_keycloak = AsyncMock()
        mock_keycloak.enable_user.return_value = True

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_keycloak_admin] = lambda: mock_keycloak

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/users/user-1-uuid/status',
                json={'enabled': True},
            )
            assert response.status_code == 200

        app.dependency_overrides.clear()


class TestAdminBulkOperations:
    """Tests for POST /api/v1/admin/users/bulk endpoint."""

    async def test_bulk_operations_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from bulk operations."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/admin/users/bulk',
                json={
                    'user_ids': ['user-1-uuid', 'user-2-uuid'],
                    'operation': 'assign_role',
                    'role': 'manager',
                },
            )
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_bulk_role_assignment(self, admin_user):
        """Admin should be able to bulk assign roles."""
        mock_keycloak = AsyncMock()
        mock_keycloak.assign_role.return_value = True

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_keycloak_admin] = lambda: mock_keycloak

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/admin/users/bulk',
                json={
                    'user_ids': ['user-1-uuid', 'user-2-uuid'],
                    'operation': 'assign_role',
                    'role': 'manager',
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data['processed'] == 2

        app.dependency_overrides.clear()

    async def test_bulk_manager_assignment(self, admin_user):
        """Admin should be able to bulk assign manager."""
        mock_keycloak = AsyncMock()
        mock_keycloak.update_user_manager.return_value = True

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_keycloak_admin] = lambda: mock_keycloak

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/admin/users/bulk',
                json={
                    'user_ids': ['user-1-uuid', 'user-2-uuid'],
                    'operation': 'assign_manager',
                    'manager_id': 'new-manager-uuid',
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data['processed'] == 2

        app.dependency_overrides.clear()
