# TSS PPM v3.0 - Manager API Tests
"""Tests for Manager API endpoints."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db


class TestManagerTeamEndpoint:
    """Tests for GET /api/v1/manager/team endpoint."""

    @pytest.fixture
    def mock_manager_user(self):
        """Mock authenticated manager user."""
        return CurrentUser(
            keycloak_id='test-manager-id',
            email='manager@example.com',
            name='Test Manager',
            roles=['employee', 'manager'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_employee_user(self):
        """Mock authenticated employee user (non-manager)."""
        return CurrentUser(
            keycloak_id='test-employee-id',
            email='employee@example.com',
            name='Test Employee',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def sample_team_member(self):
        """Sample team member data."""
        return {
            'id': uuid4(),
            'email': 'team-member@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'function_title': 'Software Engineer',
            'tov_level': 'B',
            'review_id': uuid4(),
            'review_stage': 'END_YEAR_REVIEW',
            'review_status': 'DRAFT',
            'goals_count': 5,
            'scored_goals_count': 0,
            'competency_scores_count': 0,
        }

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    async def manager_client(self, mock_manager_user, mock_db_conn):
        """Async HTTP client with manager authentication."""
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest.fixture
    async def employee_client(self, mock_employee_user, mock_db_conn):
        """Async HTTP client with employee authentication (no manager role)."""
        app.dependency_overrides[get_current_user] = lambda: mock_employee_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest.fixture
    async def unauthenticated_client(self):
        """Async HTTP client without auth override."""
        app.dependency_overrides.clear()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    # --- GET /api/v1/manager/team tests ---

    async def test_get_team_requires_auth(self, unauthenticated_client):
        """GET /manager/team should require authentication."""
        response = await unauthenticated_client.get('/api/v1/manager/team')
        assert response.status_code in [401, 403]

    async def test_get_team_requires_manager_role(self, employee_client):
        """GET /manager/team should require manager role."""
        response = await employee_client.get('/api/v1/manager/team')
        assert response.status_code == 403
        assert 'manager' in response.json().get('detail', '').lower()

    async def test_get_team_returns_list(
        self, manager_client, mock_db_conn, sample_team_member
    ):
        """GET /manager/team should return list of team members."""
        mock_db_conn.fetch.return_value = [sample_team_member]

        response = await manager_client.get('/api/v1/manager/team')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['email'] == 'team-member@example.com'
        assert data[0]['first_name'] == 'John'
        assert data[0]['last_name'] == 'Doe'

    async def test_get_team_empty_list(self, manager_client, mock_db_conn):
        """GET /manager/team should return empty list when no team members."""
        mock_db_conn.fetch.return_value = []

        response = await manager_client.get('/api/v1/manager/team')

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_get_team_includes_scoring_status(
        self, manager_client, mock_db_conn, sample_team_member
    ):
        """GET /manager/team should include scoring_status field."""
        mock_db_conn.fetch.return_value = [sample_team_member]

        response = await manager_client.get('/api/v1/manager/team')

        assert response.status_code == 200
        data = response.json()
        assert 'scoring_status' in data[0]
        # With 0 scored goals and 0 competency scores, status should be NOT_STARTED
        assert data[0]['scoring_status'] == 'NOT_STARTED'

    async def test_get_team_with_review_year_filter(
        self, manager_client, mock_db_conn, sample_team_member
    ):
        """GET /manager/team should support review_year query param."""
        mock_db_conn.fetch.return_value = [sample_team_member]

        response = await manager_client.get('/api/v1/manager/team?review_year=2026')

        assert response.status_code == 200
        # Verify the query was called with review_year parameter
        call_args = mock_db_conn.fetch.call_args
        assert 2026 in call_args[0][1:]

    async def test_get_team_response_schema(
        self, manager_client, mock_db_conn, sample_team_member
    ):
        """GET /manager/team should return proper response schema."""
        mock_db_conn.fetch.return_value = [sample_team_member]

        response = await manager_client.get('/api/v1/manager/team')

        assert response.status_code == 200
        data = response.json()[0]

        # Verify all expected fields are present
        expected_fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'function_title',
            'tov_level',
            'review_id',
            'review_stage',
            'review_status',
            'scoring_status',
        ]
        for field in expected_fields:
            assert field in data, f'Field {field} missing from response'
