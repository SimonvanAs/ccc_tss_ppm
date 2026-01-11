# TSS PPM v3.0 - System Configuration API Tests
"""Tests for system configuration and health endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db

pytestmark = pytest.mark.asyncio

# Test UUIDs
OPCO_UUID = '11111111-1111-1111-1111-111111111111'
ADMIN_UUID = '22222222-2222-2222-2222-222222222222'
USER_UUID = '33333333-3333-3333-3333-333333333333'


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


class TestSystemHealth:
    """Tests for GET /api/v1/admin/system/health endpoint."""

    async def test_health_requires_admin_role(self, non_admin_user):
        """Non-admin users should be forbidden from viewing system health."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/system/health')
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_health_returns_service_status(self, admin_user):
        """Admin users should be able to view system health."""
        mock_db = AsyncMock()
        mock_db.fetchval.return_value = 1  # DB is healthy

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/system/health')
            assert response.status_code == 200
            data = response.json()
            assert 'services' in data
            assert 'api' in data['services']
            assert 'database' in data['services']

        app.dependency_overrides.clear()

    async def test_health_includes_all_services(self, admin_user):
        """Health check should include all monitored services."""
        mock_db = AsyncMock()
        mock_db.fetchval.return_value = 1

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/system/health')
            assert response.status_code == 200
            data = response.json()
            services = data['services']
            assert 'api' in services
            assert 'database' in services
            assert 'keycloak' in services
            assert 'voice' in services

        app.dependency_overrides.clear()


class TestVoiceConfig:
    """Tests for voice configuration endpoints."""

    async def test_get_voice_config_requires_admin(self, non_admin_user):
        """Non-admin users should be forbidden from viewing voice config."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/system/voice-config')
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_get_voice_config_returns_settings(self, admin_user):
        """Admin users should be able to view voice configuration."""
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = {
            'voice_service_url': 'http://whisper:8001',
            'voice_service_enabled': True,
            'voice_model': 'whisper-small',
        }

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/system/voice-config')
            assert response.status_code == 200
            data = response.json()
            assert 'voice_service_url' in data
            assert 'voice_service_enabled' in data

        app.dependency_overrides.clear()

    async def test_update_voice_config_requires_admin(self, non_admin_user):
        """Non-admin users should be forbidden from updating voice config."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/system/voice-config',
                json={'voice_service_url': 'http://new-whisper:8001'},
            )
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_update_voice_config_updates_settings(self, admin_user):
        """Admin users should be able to update voice configuration."""
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = {
            'voice_service_url': 'http://new-whisper:8001',
            'voice_service_enabled': True,
            'voice_model': 'whisper-medium',
        }
        mock_db.execute.return_value = None

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/system/voice-config',
                json={
                    'voice_service_url': 'http://new-whisper:8001',
                    'voice_model': 'whisper-medium',
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data['voice_service_url'] == 'http://new-whisper:8001'

        app.dependency_overrides.clear()


class TestReviewPeriods:
    """Tests for review period configuration endpoints."""

    async def test_get_review_periods_requires_admin(self, non_admin_user):
        """Non-admin users should be forbidden from viewing review periods."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/system/review-periods')
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_get_review_periods_returns_periods(self, admin_user):
        """Admin users should be able to view review periods."""
        mock_db = AsyncMock()
        mock_db.fetch.return_value = [
            {
                'id': '1',
                'year': 2025,
                'stage': 'GOAL_SETTING',
                'start_date': '2025-01-15',
                'end_date': '2025-02-28',
                'is_open': True,
            },
            {
                'id': '2',
                'year': 2025,
                'stage': 'MID_YEAR_REVIEW',
                'start_date': '2025-06-01',
                'end_date': '2025-07-31',
                'is_open': False,
            },
        ]

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get('/api/v1/admin/system/review-periods')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]['stage'] == 'GOAL_SETTING'

        app.dependency_overrides.clear()

    async def test_update_review_periods_requires_admin(self, non_admin_user):
        """Non-admin users should be forbidden from updating review periods."""
        app.dependency_overrides[get_current_user] = lambda: non_admin_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/system/review-periods',
                json={'periods': []},
            )
            assert response.status_code == 403

        app.dependency_overrides.clear()

    async def test_update_review_periods_updates_config(self, admin_user):
        """Admin users should be able to update review periods."""
        mock_db = AsyncMock()
        mock_db.execute.return_value = None
        mock_db.fetch.return_value = [
            {
                'id': '1',
                'year': 2025,
                'stage': 'GOAL_SETTING',
                'start_date': '2025-02-01',
                'end_date': '2025-03-15',
                'is_open': True,
            },
        ]
        # Mock audit log insert
        mock_db.fetchrow.return_value = {'id': 1}

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.put(
                '/api/v1/admin/system/review-periods',
                json={
                    'periods': [
                        {
                            'year': 2025,
                            'stage': 'GOAL_SETTING',
                            'start_date': '2025-02-01',
                            'end_date': '2025-03-15',
                            'is_open': True,
                        },
                    ],
                },
            )
            assert response.status_code == 200

        app.dependency_overrides.clear()

    async def test_toggle_period_status(self, admin_user):
        """Admin should be able to open/close a review period."""
        from uuid import UUID
        mock_db = AsyncMock()
        # First call is for audit log, second is for fetching the period
        mock_db.fetchrow.side_effect = [
            {
                'id': UUID('11111111-1111-1111-1111-111111111111'),
                'year': 2025,
                'stage': 'GOAL_SETTING',
                'start_date': '2025-01-15',
                'end_date': '2025-02-28',
                'is_open': False,
            },
            {'id': 1},  # audit log return
        ]
        mock_db.execute.return_value = None

        app.dependency_overrides[get_current_user] = lambda: admin_user
        app.dependency_overrides[get_db] = lambda: mock_db

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/admin/system/review-periods/11111111-1111-1111-1111-111111111111/toggle',
                json={'is_open': False},
            )
            assert response.status_code == 200
            data = response.json()
            assert data['is_open'] == False

        app.dependency_overrides.clear()
