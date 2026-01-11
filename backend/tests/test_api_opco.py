# TSS PPM v3.0 - OpCo Settings API Tests
"""Tests for OpCo settings and business units API endpoints."""

from unittest.mock import AsyncMock, MagicMock
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db

pytestmark = pytest.mark.asyncio


from uuid import UUID

# Test UUIDs
OPCO_UUID = '11111111-1111-1111-1111-111111111111'
ADMIN_UUID = '22222222-2222-2222-2222-222222222222'
USER_UUID = '33333333-3333-3333-3333-333333333333'
BU1_UUID = '44444444-4444-4444-4444-444444444444'
BU2_UUID = '55555555-5555-5555-5555-555555555555'
BU3_UUID = '66666666-6666-6666-6666-666666666666'


@pytest.fixture
def admin_user():
    """Create an admin user for testing."""
    return CurrentUser(
        keycloak_id=ADMIN_UUID,
        email='admin@tss.eu',
        name='Admin User',
        roles=['admin'],
        opco_id=OPCO_UUID,
    )


@pytest.fixture
def non_admin_user():
    """Create a non-admin user for testing."""
    return CurrentUser(
        keycloak_id=USER_UUID,
        email='user@tss.eu',
        name='Regular User',
        roles=['employee'],
        opco_id=OPCO_UUID,
    )


@pytest.fixture
def sample_opco():
    """Sample OpCo data."""
    return {
        'id': UUID(OPCO_UUID),
        'name': 'TSS Netherlands',
        'code': 'TSS-NL',
        'logo_url': 'https://storage.tss.eu/logos/tss-nl.png',
        'default_language': 'nl',
        'settings': {
            'review_cycle': {
                'goal_setting_start': '2025-01-15',
                'goal_setting_end': '2025-02-28',
                'mid_year_start': '2025-06-01',
                'mid_year_end': '2025-07-31',
                'end_year_start': '2025-11-01',
                'end_year_end': '2025-12-31',
            },
        },
    }


@pytest.fixture
def sample_business_units():
    """Sample business units data."""
    return [
        {
            'id': UUID(BU1_UUID),
            'opco_id': UUID(OPCO_UUID),
            'name': 'Engineering',
            'code': 'ENG',
            'parent_id': None,
        },
        {
            'id': UUID(BU2_UUID),
            'opco_id': UUID(OPCO_UUID),
            'name': 'Product',
            'code': 'PROD',
            'parent_id': None,
        },
        {
            'id': UUID(BU3_UUID),
            'opco_id': UUID(OPCO_UUID),
            'name': 'Backend Team',
            'code': 'ENG-BE',
            'parent_id': UUID(BU1_UUID),
        },
    ]


class TestOpCoSettingsGet:
    """Tests for GET /api/v1/admin/opco/settings endpoint."""

    async def test_get_settings_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from viewing OpCo settings."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/opco/settings')
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_get_settings_returns_opco_settings(self, admin_user, sample_opco):
        """Admin users should be able to view OpCo settings."""
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = sample_opco

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/opco/settings')
            assert response.status_code == 200
            data = response.json()
            assert data['name'] == 'TSS Netherlands'
            assert data['code'] == 'TSS-NL'
            assert data['default_language'] == 'nl'

        app.dependency_overrides.clear()

    async def test_get_settings_includes_review_cycle(self, admin_user, sample_opco):
        """Settings should include review cycle configuration."""
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = sample_opco

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/opco/settings')
            assert response.status_code == 200
            data = response.json()
            assert 'review_cycle' in data['settings']

        app.dependency_overrides.clear()


class TestOpCoSettingsUpdate:
    """Tests for PUT /api/v1/admin/opco/settings endpoint."""

    async def test_update_settings_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from updating OpCo settings."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/opco/settings',
                json={'name': 'New Name'},
            )
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_update_settings_updates_opco(self, admin_user, sample_opco):
        """Admin users should be able to update OpCo settings."""
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = {**sample_opco, 'name': 'TSS Belgium'}
        mock_db.execute.return_value = None

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/opco/settings',
                json={
                    'name': 'TSS Belgium',
                    'default_language': 'nl',
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data['name'] == 'TSS Belgium'

        app.dependency_overrides.clear()

    async def test_update_review_cycle_settings(self, admin_user, sample_opco):
        """Admin should be able to update review cycle configuration."""
        updated_opco = {
            **sample_opco,
            'settings': {
                'review_cycle': {
                    'goal_setting_start': '2025-02-01',
                    'goal_setting_end': '2025-03-15',
                },
            },
        }
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = updated_opco
        mock_db.execute.return_value = None

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/opco/settings',
                json={
                    'settings': {
                        'review_cycle': {
                            'goal_setting_start': '2025-02-01',
                            'goal_setting_end': '2025-03-15',
                        },
                    },
                },
            )
            assert response.status_code == 200

        app.dependency_overrides.clear()


class TestBusinessUnitsList:
    """Tests for GET /api/v1/admin/business-units endpoint."""

    async def test_list_business_units_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from listing business units."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/business-units')
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_list_business_units_returns_units(
        self,
        admin_user,
        sample_business_units,
    ):
        """Admin users should be able to list business units."""
        mock_db = AsyncMock()
        mock_db.fetch.return_value = sample_business_units

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/business-units')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3

        app.dependency_overrides.clear()


class TestBusinessUnitsCreate:
    """Tests for POST /api/v1/admin/business-units endpoint."""

    async def test_create_business_unit_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from creating business units."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/admin/business-units',
                json={'name': 'New Unit', 'code': 'NEW'},
            )
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_create_business_unit_creates_unit(self, admin_user):
        """Admin users should be able to create business units."""
        new_unit = {
            'id': UUID('77777777-7777-7777-7777-777777777777'),
            'opco_id': UUID(OPCO_UUID),
            'name': 'Marketing',
            'code': 'MKT',
            'parent_id': None,
        }
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = new_unit

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/admin/business-units',
                json={'name': 'Marketing', 'code': 'MKT'},
            )
            assert response.status_code == 201
            data = response.json()
            assert data['name'] == 'Marketing'
            assert data['code'] == 'MKT'

        app.dependency_overrides.clear()

    async def test_create_business_unit_with_parent(self, admin_user):
        """Admin should be able to create business unit with parent."""
        new_unit = {
            'id': UUID('88888888-8888-8888-8888-888888888888'),
            'opco_id': UUID(OPCO_UUID),
            'name': 'Frontend Team',
            'code': 'ENG-FE',
            'parent_id': UUID(BU1_UUID),
        }
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = new_unit

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/admin/business-units',
                json={
                    'name': 'Frontend Team',
                    'code': 'ENG-FE',
                    'parent_id': BU1_UUID,
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert data['parent_id'] == BU1_UUID

        app.dependency_overrides.clear()


class TestBusinessUnitsUpdate:
    """Tests for PUT /api/v1/admin/business-units/{id} endpoint."""

    async def test_update_business_unit_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from updating business units."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                f'/api/v1/admin/business-units/{BU1_UUID}',
                json={'name': 'Updated Name'},
            )
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_update_business_unit_updates_unit(self, admin_user):
        """Admin users should be able to update business units."""
        updated_unit = {
            'id': UUID(BU1_UUID),
            'opco_id': UUID(OPCO_UUID),
            'name': 'Engineering & DevOps',
            'code': 'ENG',
            'parent_id': None,
        }
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = updated_unit
        mock_db.execute.return_value = None

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                f'/api/v1/admin/business-units/{BU1_UUID}',
                json={'name': 'Engineering & DevOps'},
            )
            assert response.status_code == 200
            data = response.json()
            assert data['name'] == 'Engineering & DevOps'

        app.dependency_overrides.clear()


class TestBusinessUnitsDelete:
    """Tests for DELETE /api/v1/admin/business-units/{id} endpoint."""

    async def test_delete_business_unit_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from deleting business units."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.delete(f'/api/v1/admin/business-units/{BU1_UUID}')
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_delete_business_unit_deletes_unit(self, admin_user):
        """Admin users should be able to delete business units."""
        mock_db = AsyncMock()
        # No users assigned to this unit
        mock_db.fetchval.return_value = 0
        mock_db.execute.return_value = None

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.delete(f'/api/v1/admin/business-units/{BU1_UUID}')
            assert response.status_code == 204

        app.dependency_overrides.clear()

    async def test_delete_business_unit_rejects_when_users_assigned(self, admin_user):
        """Delete should be rejected when users are assigned to the unit."""
        mock_db = AsyncMock()
        # 5 users assigned to this unit
        mock_db.fetchval.return_value = 5

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.delete(f'/api/v1/admin/business-units/{BU1_UUID}')
            assert response.status_code == 409
            data = response.json()
            assert 'users assigned' in data['detail'].lower()

        app.dependency_overrides.clear()
