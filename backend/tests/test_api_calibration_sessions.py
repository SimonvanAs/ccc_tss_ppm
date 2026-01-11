# TSS PPM v3.0 - Calibration Sessions API Tests
"""Tests for calibration session API endpoints."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db


@pytest.mark.asyncio
class TestCalibrationSessionsAPI:
    """Tests for calibration sessions API endpoints."""

    @pytest.fixture
    def sample_opco_id(self):
        """Sample OpCo ID as UUID."""
        return uuid4()

    @pytest.fixture
    def mock_hr_user(self, sample_opco_id):
        """Mock authenticated HR user."""
        return CurrentUser(
            keycloak_id='test-hr-id',
            email='hr@example.com',
            name='HR User',
            roles=['employee', 'hr'],
            opco_id=str(sample_opco_id),
        )

    @pytest.fixture
    def mock_manager_user(self, sample_opco_id):
        """Mock authenticated manager user (not HR)."""
        return CurrentUser(
            keycloak_id='test-manager-id',
            email='manager@example.com',
            name='Test Manager',
            roles=['employee', 'manager'],
            opco_id=str(sample_opco_id),
        )

    @pytest.fixture
    def mock_employee_user(self, sample_opco_id):
        """Mock authenticated employee user."""
        return CurrentUser(
            keycloak_id='test-employee-id',
            email='employee@example.com',
            name='Test Employee',
            roles=['employee'],
            opco_id=str(sample_opco_id),
        )

    @pytest.fixture
    def sample_session(self):
        """Sample calibration session data."""
        return {
            'id': uuid4(),
            'opco_id': uuid4(),
            'name': 'Q4 2026 Calibration',
            'description': 'End of year calibration session',
            'review_year': 2026,
            'scope': 'COMPANY_WIDE',
            'business_unit_id': None,
            'status': 'PREPARATION',
            'facilitator_id': uuid4(),
            'created_by': uuid4(),
            'snapshot_taken_at': None,
            'completed_at': None,
            'notes': None,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest_asyncio.fixture
    async def hr_client(self, mock_hr_user, mock_db_conn):
        """Async HTTP client with HR authentication."""
        app.dependency_overrides[get_current_user] = lambda: mock_hr_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def manager_client(self, mock_manager_user, mock_db_conn):
        """Async HTTP client with manager authentication (not HR)."""
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def unauthenticated_client(self):
        """Async HTTP client without auth."""
        app.dependency_overrides.clear()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    # --- Authorization Tests ---

    async def test_create_session_requires_auth(self, unauthenticated_client):
        """POST /calibration-sessions should require authentication."""
        response = await unauthenticated_client.post(
            '/api/v1/calibration-sessions',
            json={'name': 'Test', 'review_year': 2026, 'scope': 'COMPANY_WIDE'}
        )
        # FastAPI returns 403 when auth dependency fails (no valid token)
        assert response.status_code in (401, 403)

    async def test_create_session_requires_hr_role(self, manager_client):
        """POST /calibration-sessions should require HR role."""
        response = await manager_client.post(
            '/api/v1/calibration-sessions',
            json={'name': 'Test', 'review_year': 2026, 'scope': 'COMPANY_WIDE'}
        )
        assert response.status_code == 403

    async def test_list_sessions_requires_hr_role(self, manager_client):
        """GET /calibration-sessions should require HR role."""
        response = await manager_client.get('/api/v1/calibration-sessions')
        assert response.status_code == 403

    # --- Create Session Tests ---

    async def test_create_session_success(self, hr_client, mock_db_conn, sample_session):
        """POST /calibration-sessions should create a session."""
        mock_db_conn.fetchrow.return_value = sample_session

        response = await hr_client.post(
            '/api/v1/calibration-sessions',
            json={
                'name': 'Q4 2026 Calibration',
                'description': 'End of year calibration session',
                'review_year': 2026,
                'scope': 'COMPANY_WIDE',
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data['name'] == 'Q4 2026 Calibration'
        assert data['status'] == 'PREPARATION'

    async def test_create_session_with_business_unit(self, hr_client, mock_db_conn, sample_session):
        """POST /calibration-sessions should allow business unit scope."""
        sample_session['scope'] = 'BUSINESS_UNIT'
        sample_session['business_unit_id'] = uuid4()
        mock_db_conn.fetchrow.return_value = sample_session

        response = await hr_client.post(
            '/api/v1/calibration-sessions',
            json={
                'name': 'BU Calibration',
                'review_year': 2026,
                'scope': 'BUSINESS_UNIT',
                'business_unit_id': str(sample_session['business_unit_id']),
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data['scope'] == 'BUSINESS_UNIT'

    async def test_create_session_validation_error(self, hr_client):
        """POST /calibration-sessions should validate required fields."""
        response = await hr_client.post(
            '/api/v1/calibration-sessions',
            json={'name': 'Test'}  # Missing required fields
        )

        assert response.status_code == 422

    # --- List Sessions Tests ---

    async def test_list_sessions_success(self, hr_client, mock_db_conn, sample_session):
        """GET /calibration-sessions should return sessions for OpCo."""
        mock_db_conn.fetch.return_value = [sample_session]

        response = await hr_client.get('/api/v1/calibration-sessions')

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'Q4 2026 Calibration'

    async def test_list_sessions_filter_by_status(self, hr_client, mock_db_conn, sample_session):
        """GET /calibration-sessions should filter by status."""
        mock_db_conn.fetch.return_value = [sample_session]

        response = await hr_client.get(
            '/api/v1/calibration-sessions',
            params={'status': 'PREPARATION'}
        )

        assert response.status_code == 200

    async def test_list_sessions_filter_by_year(self, hr_client, mock_db_conn, sample_session):
        """GET /calibration-sessions should filter by year."""
        mock_db_conn.fetch.return_value = [sample_session]

        response = await hr_client.get(
            '/api/v1/calibration-sessions',
            params={'review_year': 2026}
        )

        assert response.status_code == 200

    async def test_list_sessions_empty(self, hr_client, mock_db_conn):
        """GET /calibration-sessions should return empty list when no sessions."""
        mock_db_conn.fetch.return_value = []

        response = await hr_client.get('/api/v1/calibration-sessions')

        assert response.status_code == 200
        assert response.json() == []

    # --- Get Session Tests ---

    async def test_get_session_success(self, hr_client, mock_db_conn, sample_session):
        """GET /calibration-sessions/{id} should return session."""
        mock_db_conn.fetchrow.return_value = sample_session
        session_id = str(sample_session['id'])

        response = await hr_client.get(f'/api/v1/calibration-sessions/{session_id}')

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Q4 2026 Calibration'

    async def test_get_session_not_found(self, hr_client, mock_db_conn):
        """GET /calibration-sessions/{id} should return 404 when not found."""
        mock_db_conn.fetchrow.return_value = None
        session_id = str(uuid4())

        response = await hr_client.get(f'/api/v1/calibration-sessions/{session_id}')

        assert response.status_code == 404

    # --- Update Session Tests ---

    async def test_update_session_success(self, hr_client, mock_db_conn, sample_session):
        """PUT /calibration-sessions/{id} should update session."""
        updated_session = {**sample_session, 'name': 'Updated Name'}
        mock_db_conn.fetchrow.return_value = updated_session
        session_id = str(sample_session['id'])

        response = await hr_client.put(
            f'/api/v1/calibration-sessions/{session_id}',
            json={'name': 'Updated Name'}
        )

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Updated Name'

    async def test_update_session_not_found(self, hr_client, mock_db_conn):
        """PUT /calibration-sessions/{id} should return 404 when not found."""
        mock_db_conn.fetchrow.return_value = None
        session_id = str(uuid4())

        response = await hr_client.put(
            f'/api/v1/calibration-sessions/{session_id}',
            json={'name': 'New Name'}
        )

        assert response.status_code == 404

    # --- Delete Session Tests ---

    async def test_delete_session_success(self, hr_client, mock_db_conn, sample_session):
        """DELETE /calibration-sessions/{id} should delete draft session."""
        mock_db_conn.fetchrow.return_value = sample_session
        mock_db_conn.execute.return_value = 'DELETE 1'
        session_id = str(sample_session['id'])

        response = await hr_client.delete(f'/api/v1/calibration-sessions/{session_id}')

        assert response.status_code == 204

    async def test_delete_session_not_draft(self, hr_client, mock_db_conn, sample_session):
        """DELETE /calibration-sessions/{id} should reject non-draft session."""
        sample_session['status'] = 'IN_PROGRESS'
        mock_db_conn.fetchrow.return_value = sample_session
        session_id = str(sample_session['id'])

        response = await hr_client.delete(f'/api/v1/calibration-sessions/{session_id}')

        assert response.status_code == 400

    async def test_delete_session_not_found(self, hr_client, mock_db_conn):
        """DELETE /calibration-sessions/{id} should return 404 when not found."""
        mock_db_conn.fetchrow.return_value = None
        session_id = str(uuid4())

        response = await hr_client.delete(f'/api/v1/calibration-sessions/{session_id}')

        assert response.status_code == 404

    # --- Status Transition Tests ---

    async def test_start_session_success(self, hr_client, mock_db_conn, sample_session):
        """POST /calibration-sessions/{id}/start should start session."""
        # 3 fetchrow calls: router get_session, repo.start_session get_session, repo.start_session update
        mock_db_conn.fetchrow.side_effect = [
            sample_session,  # Router: get_session_by_id with opco_id
            sample_session,  # Repo: start_session -> get_session_by_id
            {**sample_session, 'status': 'IN_PROGRESS'}  # Repo: start_session -> UPDATE
        ]
        session_id = str(sample_session['id'])

        response = await hr_client.post(f'/api/v1/calibration-sessions/{session_id}/start')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'IN_PROGRESS'

    async def test_start_session_invalid_status(self, hr_client, mock_db_conn, sample_session):
        """POST /calibration-sessions/{id}/start should reject non-preparation session."""
        sample_session['status'] = 'COMPLETED'
        mock_db_conn.fetchrow.return_value = sample_session
        session_id = str(sample_session['id'])

        response = await hr_client.post(f'/api/v1/calibration-sessions/{session_id}/start')

        assert response.status_code == 400

    async def test_complete_session_success(self, hr_client, mock_db_conn, sample_session):
        """POST /calibration-sessions/{id}/complete should complete session."""
        sample_session['status'] = 'IN_PROGRESS'
        # 3 fetchrow calls: router get_session, repo.complete_session get_session, repo.complete_session update
        mock_db_conn.fetchrow.side_effect = [
            sample_session,  # Router: get_session_by_id with opco_id
            sample_session,  # Repo: complete_session -> get_session_by_id
            {**sample_session, 'status': 'COMPLETED'}  # Repo: complete_session -> UPDATE
        ]
        session_id = str(sample_session['id'])

        response = await hr_client.post(f'/api/v1/calibration-sessions/{session_id}/complete')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'COMPLETED'

    async def test_complete_session_invalid_status(self, hr_client, mock_db_conn, sample_session):
        """POST /calibration-sessions/{id}/complete should reject preparation session."""
        sample_session['status'] = 'PREPARATION'
        mock_db_conn.fetchrow.return_value = sample_session
        session_id = str(sample_session['id'])

        response = await hr_client.post(f'/api/v1/calibration-sessions/{session_id}/complete')

        assert response.status_code == 400

    # --- OpCo Isolation Tests ---

    async def test_opco_isolation_list_sessions(self, hr_client, mock_db_conn):
        """Sessions should be filtered by user's OpCo."""
        mock_db_conn.fetch.return_value = []

        response = await hr_client.get('/api/v1/calibration-sessions')

        assert response.status_code == 200
        # Verify OpCo filter is applied (mock was called)
        mock_db_conn.fetch.assert_called_once()

    async def test_opco_isolation_get_session(self, hr_client, mock_db_conn, sample_session):
        """Session retrieval should respect OpCo isolation."""
        mock_db_conn.fetchrow.return_value = sample_session
        session_id = str(sample_session['id'])

        response = await hr_client.get(f'/api/v1/calibration-sessions/{session_id}')

        assert response.status_code == 200
        # Verify the query included OpCo filter
        call_args = mock_db_conn.fetchrow.call_args[0][0]
        assert 'opco_id' in call_args
