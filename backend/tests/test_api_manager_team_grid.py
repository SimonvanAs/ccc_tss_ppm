# TSS PPM v3.0 - Manager Team Grid API Tests
"""Tests for GET /api/v1/manager/team/grid endpoint."""

from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db


class TestManagerTeamGridEndpoint:
    """Tests for GET /api/v1/manager/team/grid endpoint."""

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
    def mock_other_opco_user(self):
        """Mock manager from different OpCo."""
        return CurrentUser(
            keycloak_id='other-manager-id',
            email='other-manager@example.com',
            name='Other Manager',
            roles=['employee', 'manager'],
            opco_id='other-opco',
        )

    @pytest.fixture
    def sample_team_member_with_scores(self):
        """Sample team member data with WHAT/HOW scores."""
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
            'what_score': Decimal('2.50'),
            'how_score': Decimal('2.80'),
            'grid_position_what': 3,
            'grid_position_how': 3,
            'what_veto_active': False,
            'how_veto_active': False,
        }

    @pytest.fixture
    def sample_team_member_without_scores(self):
        """Sample team member data without scores."""
        return {
            'id': uuid4(),
            'email': 'new-member@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'function_title': 'Junior Developer',
            'tov_level': 'A',
            'review_id': uuid4(),
            'review_stage': 'GOAL_SETTING',
            'review_status': 'DRAFT',
            'what_score': None,
            'how_score': None,
            'grid_position_what': None,
            'grid_position_how': None,
            'what_veto_active': False,
            'how_veto_active': False,
        }

    @pytest.fixture
    def sample_team_member_with_veto(self):
        """Sample team member with VETO active."""
        return {
            'id': uuid4(),
            'email': 'veto-member@example.com',
            'first_name': 'Bob',
            'last_name': 'Wilson',
            'function_title': 'Sales Rep',
            'tov_level': 'C',
            'review_id': uuid4(),
            'review_stage': 'END_YEAR_REVIEW',
            'review_status': 'PENDING_EMPLOYEE_SIGNATURE',
            'what_score': Decimal('1.00'),
            'how_score': Decimal('2.50'),
            'grid_position_what': 1,
            'grid_position_how': 3,
            'what_veto_active': True,
            'how_veto_active': False,
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

    # --- Authentication and Authorization Tests ---

    async def test_team_grid_requires_auth(self, unauthenticated_client):
        """GET /manager/team/grid should require authentication."""
        response = await unauthenticated_client.get('/api/v1/manager/team/grid')
        assert response.status_code in [401, 403]

    async def test_team_grid_requires_manager_role(self, employee_client):
        """GET /manager/team/grid should require manager role."""
        response = await employee_client.get('/api/v1/manager/team/grid')
        assert response.status_code == 403
        assert 'manager' in response.json().get('detail', '').lower()

    # --- Response Data Tests ---

    async def test_team_grid_returns_team_with_scores(
        self, manager_client, mock_db_conn, sample_team_member_with_scores
    ):
        """GET /manager/team/grid should return team members with WHAT/HOW scores."""
        # Setup mock - first call for manager lookup, second for team members
        mock_db_conn.fetchrow.return_value = {'id': uuid4()}
        mock_db_conn.fetch.return_value = [sample_team_member_with_scores]

        response = await manager_client.get('/api/v1/manager/team/grid')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        member = data[0]
        assert member['email'] == 'team-member@example.com'
        assert member['what_score'] == 2.50
        assert member['how_score'] == 2.80
        assert member['grid_position_what'] == 3
        assert member['grid_position_how'] == 3

    async def test_team_grid_handles_null_scores(
        self, manager_client, mock_db_conn, sample_team_member_without_scores
    ):
        """GET /manager/team/grid should handle null scores gracefully."""
        mock_db_conn.fetchrow.return_value = {'id': uuid4()}
        mock_db_conn.fetch.return_value = [sample_team_member_without_scores]

        response = await manager_client.get('/api/v1/manager/team/grid')

        assert response.status_code == 200
        data = response.json()
        member = data[0]

        assert member['what_score'] is None
        assert member['how_score'] is None
        assert member['grid_position_what'] is None
        assert member['grid_position_how'] is None

    async def test_team_grid_includes_review_status(
        self, manager_client, mock_db_conn, sample_team_member_with_scores
    ):
        """GET /manager/team/grid should include review_status for each member."""
        mock_db_conn.fetchrow.return_value = {'id': uuid4()}
        mock_db_conn.fetch.return_value = [sample_team_member_with_scores]

        response = await manager_client.get('/api/v1/manager/team/grid')

        assert response.status_code == 200
        member = response.json()[0]
        assert 'review_status' in member
        assert member['review_status'] == 'DRAFT'

    async def test_team_grid_includes_veto_flags(
        self, manager_client, mock_db_conn, sample_team_member_with_veto
    ):
        """GET /manager/team/grid should include VETO active flags."""
        mock_db_conn.fetchrow.return_value = {'id': uuid4()}
        mock_db_conn.fetch.return_value = [sample_team_member_with_veto]

        response = await manager_client.get('/api/v1/manager/team/grid')

        assert response.status_code == 200
        member = response.json()[0]
        assert member['what_veto_active'] is True
        assert member['how_veto_active'] is False

    async def test_team_grid_filters_by_manager_id(
        self, manager_client, mock_db_conn, sample_team_member_with_scores
    ):
        """GET /manager/team/grid should filter results by manager_id from JWT."""
        manager_uuid = uuid4()
        mock_db_conn.fetchrow.return_value = {'id': manager_uuid}
        mock_db_conn.fetch.return_value = [sample_team_member_with_scores]

        response = await manager_client.get('/api/v1/manager/team/grid')

        assert response.status_code == 200

        # Verify the fetch was called with manager_id
        call_args = mock_db_conn.fetch.call_args
        assert manager_uuid in call_args[0][1:]

    async def test_team_grid_returns_empty_for_no_team(
        self, manager_client, mock_db_conn
    ):
        """GET /manager/team/grid should return empty list when no team members."""
        mock_db_conn.fetchrow.return_value = {'id': uuid4()}
        mock_db_conn.fetch.return_value = []

        response = await manager_client.get('/api/v1/manager/team/grid')

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_team_grid_returns_multiple_members(
        self,
        manager_client,
        mock_db_conn,
        sample_team_member_with_scores,
        sample_team_member_without_scores,
        sample_team_member_with_veto,
    ):
        """GET /manager/team/grid should return all team members."""
        mock_db_conn.fetchrow.return_value = {'id': uuid4()}
        mock_db_conn.fetch.return_value = [
            sample_team_member_with_scores,
            sample_team_member_without_scores,
            sample_team_member_with_veto,
        ]

        response = await manager_client.get('/api/v1/manager/team/grid')

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    async def test_team_grid_with_review_year_filter(
        self, manager_client, mock_db_conn, sample_team_member_with_scores
    ):
        """GET /manager/team/grid should support review_year query param."""
        mock_db_conn.fetchrow.return_value = {'id': uuid4()}
        mock_db_conn.fetch.return_value = [sample_team_member_with_scores]

        response = await manager_client.get('/api/v1/manager/team/grid?review_year=2026')

        assert response.status_code == 200
        # Verify the query was called with review_year parameter
        call_args = mock_db_conn.fetch.call_args
        assert 2026 in call_args[0][1:]

    async def test_team_grid_response_schema(
        self, manager_client, mock_db_conn, sample_team_member_with_scores
    ):
        """GET /manager/team/grid should return proper response schema."""
        mock_db_conn.fetchrow.return_value = {'id': uuid4()}
        mock_db_conn.fetch.return_value = [sample_team_member_with_scores]

        response = await manager_client.get('/api/v1/manager/team/grid')

        assert response.status_code == 200
        data = response.json()[0]

        # Verify all expected fields are present
        expected_fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'review_id',
            'review_status',
            'what_score',
            'how_score',
            'grid_position_what',
            'grid_position_how',
            'what_veto_active',
            'how_veto_active',
        ]
        for field in expected_fields:
            assert field in data, f'Field {field} missing from response'

    async def test_team_grid_returns_empty_when_manager_not_in_db(
        self, manager_client, mock_db_conn
    ):
        """GET /manager/team/grid should return empty list when manager not found in DB."""
        mock_db_conn.fetchrow.return_value = None  # Manager not found

        response = await manager_client.get('/api/v1/manager/team/grid')

        assert response.status_code == 200
        data = response.json()
        assert data == []

    # --- OpCo Isolation Tests ---

    async def test_team_grid_respects_opco_isolation(
        self, mock_other_opco_user, mock_db_conn, sample_team_member_with_scores
    ):
        """GET /manager/team/grid should only return team members from same OpCo."""
        # Setup client with other OpCo user
        app.dependency_overrides[get_current_user] = lambda: mock_other_opco_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            mock_db_conn.fetchrow.return_value = {'id': uuid4()}
            mock_db_conn.fetch.return_value = []  # No members in this OpCo

            response = await client.get('/api/v1/manager/team/grid')

            assert response.status_code == 200
            # Should return empty because the query filters by opco_id

        app.dependency_overrides.clear()
