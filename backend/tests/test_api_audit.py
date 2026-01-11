# TSS PPM v3.0 - Audit Log API Tests
"""Tests for admin audit log endpoints."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

from httpx import AsyncClient, ASGITransport

from src.main import app


@pytest.fixture
def admin_user():
    """Mock admin user for testing."""
    return {
        'id': UUID('11111111-1111-1111-1111-111111111111'),
        'keycloak_id': 'admin-kc-id',
        'opco_id': UUID('22222222-2222-2222-2222-222222222222'),
        'email': 'admin@example.com',
        'roles': ['admin'],
    }


@pytest.fixture
def non_admin_user():
    """Mock non-admin user for testing."""
    return {
        'id': UUID('33333333-3333-3333-3333-333333333333'),
        'keycloak_id': 'user-kc-id',
        'opco_id': UUID('22222222-2222-2222-2222-222222222222'),
        'email': 'user@example.com',
        'roles': ['employee'],
    }


@pytest.fixture
def sample_audit_logs():
    """Sample audit log entries for testing."""
    base_time = datetime.now(timezone.utc)
    return [
        {
            'id': UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
            'opco_id': UUID('22222222-2222-2222-2222-222222222222'),
            'user_id': UUID('11111111-1111-1111-1111-111111111111'),
            'action': 'UPDATE_ROLES',
            'entity_type': 'user',
            'entity_id': UUID('44444444-4444-4444-4444-444444444444'),
            'changes': {'before': {'roles': ['employee']}, 'after': {'roles': ['employee', 'manager']}},
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0',
            'created_at': base_time - timedelta(hours=1),
            'user_email': 'admin@example.com',
            'user_name': 'Admin User',
        },
        {
            'id': UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
            'opco_id': UUID('22222222-2222-2222-2222-222222222222'),
            'user_id': UUID('11111111-1111-1111-1111-111111111111'),
            'action': 'DEACTIVATE_USER',
            'entity_type': 'user',
            'entity_id': UUID('55555555-5555-5555-5555-555555555555'),
            'changes': {'before': {'enabled': True}, 'after': {'enabled': False}},
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0',
            'created_at': base_time - timedelta(hours=2),
            'user_email': 'admin@example.com',
            'user_name': 'Admin User',
        },
        {
            'id': UUID('cccccccc-cccc-cccc-cccc-cccccccccccc'),
            'opco_id': UUID('22222222-2222-2222-2222-222222222222'),
            'user_id': UUID('11111111-1111-1111-1111-111111111111'),
            'action': 'UPDATE_OPCO_SETTINGS',
            'entity_type': 'opco',
            'entity_id': UUID('22222222-2222-2222-2222-222222222222'),
            'changes': {'before': {'default_language': 'en'}, 'after': {'default_language': 'nl'}},
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0',
            'created_at': base_time - timedelta(days=1),
            'user_email': 'admin@example.com',
            'user_name': 'Admin User',
        },
    ]


class TestAuditLogList:
    """Tests for GET /api/v1/admin/audit-logs endpoint."""

    @pytest.mark.asyncio
    async def test_list_audit_logs_success(self, admin_user, sample_audit_logs):
        """Test successful retrieval of audit logs."""
        mock_db = AsyncMock()
        mock_db.fetch.return_value = sample_audit_logs
        mock_db.fetchrow.return_value = {'total': 3}

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                response = await client.get('/api/v1/admin/audit-logs')

        assert response.status_code == 200
        data = response.json()
        assert 'logs' in data
        assert 'total' in data
        assert 'page' in data
        assert 'page_size' in data
        assert len(data['logs']) == 3

    @pytest.mark.asyncio
    async def test_list_audit_logs_with_pagination(self, admin_user, sample_audit_logs):
        """Test audit logs with pagination parameters."""
        mock_db = AsyncMock()
        mock_db.fetch.return_value = sample_audit_logs[:1]
        mock_db.fetchrow.return_value = {'total': 3}

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                response = await client.get('/api/v1/admin/audit-logs?page=1&page_size=1')

        assert response.status_code == 200
        data = response.json()
        assert data['page'] == 1
        assert data['page_size'] == 1

    @pytest.mark.asyncio
    async def test_list_audit_logs_with_date_filter(self, admin_user, sample_audit_logs):
        """Test audit logs filtered by date range."""
        mock_db = AsyncMock()
        mock_db.fetch.return_value = sample_audit_logs[:2]
        mock_db.fetchrow.return_value = {'total': 2}

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                start_date = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
                end_date = datetime.now(timezone.utc).isoformat()
                response = await client.get(
                    f'/api/v1/admin/audit-logs?start_date={start_date}&end_date={end_date}'
                )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_audit_logs_with_user_filter(self, admin_user, sample_audit_logs):
        """Test audit logs filtered by user ID."""
        mock_db = AsyncMock()
        mock_db.fetch.return_value = sample_audit_logs
        mock_db.fetchrow.return_value = {'total': 3}

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                user_id = '11111111-1111-1111-1111-111111111111'
                response = await client.get(f'/api/v1/admin/audit-logs?user_id={user_id}')

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_audit_logs_with_action_filter(self, admin_user, sample_audit_logs):
        """Test audit logs filtered by action type."""
        mock_db = AsyncMock()
        mock_db.fetch.return_value = [sample_audit_logs[0]]
        mock_db.fetchrow.return_value = {'total': 1}

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                response = await client.get('/api/v1/admin/audit-logs?action=UPDATE_ROLES')

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_audit_logs_with_entity_type_filter(self, admin_user, sample_audit_logs):
        """Test audit logs filtered by entity type."""
        mock_db = AsyncMock()
        mock_db.fetch.return_value = sample_audit_logs[:2]
        mock_db.fetchrow.return_value = {'total': 2}

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                response = await client.get('/api/v1/admin/audit-logs?entity_type=user')

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_audit_logs_requires_admin(self, non_admin_user):
        """Test that non-admin users cannot access audit logs."""
        from fastapi import HTTPException

        async def raise_forbidden(*args, **kwargs):
            raise HTTPException(status_code=403, detail='Admin role required')

        with patch('src.routers.audit.require_admin', side_effect=raise_forbidden):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                response = await client.get('/api/v1/admin/audit-logs')

        assert response.status_code == 403


class TestAuditLogExport:
    """Tests for GET /api/v1/admin/audit-logs/export endpoint."""

    @pytest.mark.asyncio
    async def test_export_audit_logs_csv(self, admin_user, sample_audit_logs):
        """Test exporting audit logs as CSV."""
        mock_db = AsyncMock()
        mock_db.fetch.return_value = sample_audit_logs

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                response = await client.get('/api/v1/admin/audit-logs/export')

        assert response.status_code == 200
        assert 'text/csv' in response.headers['content-type']
        assert 'attachment' in response.headers.get('content-disposition', '')

        # Check CSV content
        content = response.text
        lines = content.strip().split('\n')
        assert len(lines) >= 2  # Header + at least one data row
        assert 'action' in lines[0].lower()
        assert 'entity_type' in lines[0].lower()

    @pytest.mark.asyncio
    async def test_export_audit_logs_with_filters(self, admin_user, sample_audit_logs):
        """Test exporting filtered audit logs."""
        mock_db = AsyncMock()
        mock_db.fetch.return_value = [sample_audit_logs[0]]

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                response = await client.get('/api/v1/admin/audit-logs/export?action=UPDATE_ROLES')

        assert response.status_code == 200
        assert 'text/csv' in response.headers['content-type']

    @pytest.mark.asyncio
    async def test_export_audit_logs_requires_admin(self, non_admin_user):
        """Test that non-admin users cannot export audit logs."""
        from fastapi import HTTPException

        async def raise_forbidden(*args, **kwargs):
            raise HTTPException(status_code=403, detail='Admin role required')

        with patch('src.routers.audit.require_admin', side_effect=raise_forbidden):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                response = await client.get('/api/v1/admin/audit-logs/export')

        assert response.status_code == 403


class TestAuditLogDetail:
    """Tests for GET /api/v1/admin/audit-logs/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_audit_log_detail(self, admin_user, sample_audit_logs):
        """Test getting a single audit log entry."""
        log_entry = sample_audit_logs[0]
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = log_entry

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                response = await client.get(f'/api/v1/admin/audit-logs/{log_entry["id"]}')

        assert response.status_code == 200
        data = response.json()
        assert data['action'] == 'UPDATE_ROLES'
        assert data['entity_type'] == 'user'

    @pytest.mark.asyncio
    async def test_get_audit_log_not_found(self, admin_user):
        """Test getting a non-existent audit log."""
        mock_db = AsyncMock()
        mock_db.fetchrow.return_value = None

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                log_id = 'ffffffff-ffff-ffff-ffff-ffffffffffff'
                response = await client.get(f'/api/v1/admin/audit-logs/{log_id}')

        assert response.status_code == 404


class TestAuditLogFilters:
    """Tests for audit log filter options endpoint."""

    @pytest.mark.asyncio
    async def test_get_filter_options(self, admin_user):
        """Test getting available filter options."""
        mock_db = AsyncMock()
        mock_db.fetch.side_effect = [
            # Action types
            [{'action': 'UPDATE_ROLES'}, {'action': 'DEACTIVATE_USER'}, {'action': 'UPDATE_OPCO_SETTINGS'}],
            # Entity types
            [{'entity_type': 'user'}, {'entity_type': 'opco'}, {'entity_type': 'business_unit'}],
        ]

        with patch('src.routers.audit.get_db', return_value=mock_db), \
             patch('src.routers.audit.require_admin', return_value=admin_user):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url='http://test'
            ) as client:
                response = await client.get('/api/v1/admin/audit-logs/filters')

        assert response.status_code == 200
        data = response.json()
        assert 'actions' in data
        assert 'entity_types' in data
        assert 'UPDATE_ROLES' in data['actions']
        assert 'user' in data['entity_types']
