# TSS PPM v3.0 - Goal API Tests
"""Tests for Goal API endpoints."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db
from src.schemas.goal import GoalType


class TestGoalAPIEndpoints:
    """Tests for Goal API endpoints."""

    @pytest.fixture
    def mock_current_user(self):
        """Mock authenticated user."""
        return CurrentUser(
            keycloak_id='test-user-id',
            email='test@example.com',
            name='Test User',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def sample_goal(self):
        """Sample goal data."""
        return {
            'id': uuid4(),
            'review_id': uuid4(),
            'title': 'Complete project',
            'description': 'Finish Q1 project',
            'goal_type': 'STANDARD',
            'weight': 25,
            'score': None,
            'display_order': 0,
        }

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    async def client(self, mock_current_user, mock_db_conn):
        """Async HTTP client with dependency overrides."""
        # Override dependencies
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        # Clear overrides after test
        app.dependency_overrides.clear()

    @pytest.fixture
    async def unauthenticated_client(self):
        """Async HTTP client without auth override."""
        # Clear any existing overrides
        app.dependency_overrides.clear()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    # --- GET /api/v1/reviews/:id/goals tests ---

    async def test_get_goals_requires_auth(self, unauthenticated_client):
        """GET /reviews/:id/goals should require authentication."""
        review_id = uuid4()
        response = await unauthenticated_client.get(f'/api/v1/reviews/{review_id}/goals')
        # FastAPI returns 403 when no credentials provided (HTTPBearer behavior)
        assert response.status_code in [401, 403]

    async def test_get_goals_returns_list(self, client, mock_db_conn, sample_goal):
        """GET /reviews/:id/goals should return list of goals."""
        review_id = uuid4()
        mock_db_conn.fetch.return_value = [sample_goal]

        response = await client.get(f'/api/v1/reviews/{review_id}/goals')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['title'] == 'Complete project'

    async def test_get_goals_empty_list(self, client, mock_db_conn):
        """GET /reviews/:id/goals should return empty list when no goals."""
        review_id = uuid4()
        mock_db_conn.fetch.return_value = []

        response = await client.get(f'/api/v1/reviews/{review_id}/goals')

        assert response.status_code == 200
        assert response.json() == []

    # --- POST /api/v1/reviews/:id/goals tests ---

    async def test_create_goal_requires_auth(self, unauthenticated_client):
        """POST /reviews/:id/goals should require authentication."""
        review_id = uuid4()
        response = await unauthenticated_client.post(
            f'/api/v1/reviews/{review_id}/goals',
            json={'title': 'New goal', 'weight': 20},
        )
        assert response.status_code in [401, 403]

    async def test_create_goal_success(self, client, mock_db_conn, sample_goal):
        """POST /reviews/:id/goals should create and return goal."""
        review_id = uuid4()
        # First fetchval for count, second for next display_order
        mock_db_conn.fetchval.side_effect = [0, 0]
        mock_db_conn.fetchrow.return_value = sample_goal

        response = await client.post(
            f'/api/v1/reviews/{review_id}/goals',
            json={'title': 'New goal', 'weight': 20},
        )

        assert response.status_code == 201
        data = response.json()
        assert 'id' in data
        assert data['title'] == 'Complete project'

    async def test_create_goal_validation_error(self, client, mock_db_conn):
        """POST /reviews/:id/goals should return 422 for invalid data."""
        review_id = uuid4()

        response = await client.post(
            f'/api/v1/reviews/{review_id}/goals',
            json={'title': '', 'weight': 3},  # Invalid: empty title, weight not multiple of 5
        )

        assert response.status_code == 422

    async def test_create_goal_max_9_goals(self, client, mock_db_conn):
        """POST /reviews/:id/goals should reject when 9 goals exist."""
        review_id = uuid4()
        mock_db_conn.fetchval.return_value = 9  # Already at max

        response = await client.post(
            f'/api/v1/reviews/{review_id}/goals',
            json={'title': 'New goal', 'weight': 20},
        )

        assert response.status_code == 400
        assert 'Maximum of 9 goals' in response.json()['detail']

    # --- PUT /api/v1/goals/:id tests ---

    async def test_update_goal_requires_auth(self, unauthenticated_client):
        """PUT /goals/:id should require authentication."""
        goal_id = uuid4()
        response = await unauthenticated_client.put(
            f'/api/v1/goals/{goal_id}',
            json={'title': 'Updated'},
        )
        assert response.status_code in [401, 403]

    async def test_update_goal_success(self, client, mock_db_conn, sample_goal):
        """PUT /goals/:id should update and return goal."""
        goal_id = uuid4()
        updated_goal = {**sample_goal, 'title': 'Updated title'}
        # First call for get_goal (check exists), second for update_goal
        mock_db_conn.fetchrow.side_effect = [sample_goal, updated_goal]

        response = await client.put(
            f'/api/v1/goals/{goal_id}',
            json={'title': 'Updated title'},
        )

        assert response.status_code == 200
        assert response.json()['title'] == 'Updated title'

    async def test_update_goal_not_found(self, client, mock_db_conn):
        """PUT /goals/:id should return 404 when goal doesn't exist."""
        goal_id = uuid4()
        mock_db_conn.fetchrow.return_value = None

        response = await client.put(
            f'/api/v1/goals/{goal_id}',
            json={'title': 'Updated'},
        )

        assert response.status_code == 404

    # --- DELETE /api/v1/goals/:id tests ---

    async def test_delete_goal_requires_auth(self, unauthenticated_client):
        """DELETE /goals/:id should require authentication."""
        goal_id = uuid4()
        response = await unauthenticated_client.delete(f'/api/v1/goals/{goal_id}')
        assert response.status_code in [401, 403]

    async def test_delete_goal_success(self, client, mock_db_conn, sample_goal):
        """DELETE /goals/:id should delete and return 204."""
        goal_id = uuid4()
        mock_db_conn.fetchrow.return_value = sample_goal  # get_goal check
        mock_db_conn.execute.return_value = 'UPDATE 1'  # delete_goal

        response = await client.delete(f'/api/v1/goals/{goal_id}')

        assert response.status_code == 204

    async def test_delete_goal_not_found(self, client, mock_db_conn):
        """DELETE /goals/:id should return 404 when goal doesn't exist."""
        goal_id = uuid4()
        mock_db_conn.fetchrow.return_value = None

        response = await client.delete(f'/api/v1/goals/{goal_id}')

        assert response.status_code == 404

    # --- PUT /api/v1/reviews/:id/goals/order tests ---

    async def test_reorder_goals_requires_auth(self, unauthenticated_client):
        """PUT /reviews/:id/goals/order should require authentication."""
        review_id = uuid4()
        response = await unauthenticated_client.put(
            f'/api/v1/reviews/{review_id}/goals/order',
            json={'goal_ids': [str(uuid4())]},
        )
        assert response.status_code in [401, 403]

    async def test_reorder_goals_success(self, client, mock_db_conn):
        """PUT /reviews/:id/goals/order should reorder goals."""
        review_id = uuid4()
        goal_ids = [uuid4(), uuid4()]

        response = await client.put(
            f'/api/v1/reviews/{review_id}/goals/order',
            json={'goal_ids': [str(g) for g in goal_ids]},
        )

        assert response.status_code == 200
        assert 'message' in response.json()


class TestGoalAPIAuthorization:
    """Tests for Goal API authorization - placeholder tests."""

    async def test_employee_can_access_own_review(self):
        """Employee should be able to access their own review's goals."""
        # Placeholder - authorization logic TBD
        pass

    async def test_employee_cannot_access_others_review(self):
        """Employee should not be able to access another's review's goals."""
        # Placeholder - authorization logic TBD
        pass

    async def test_manager_can_access_direct_reports_review(self):
        """Manager should be able to access direct report's review's goals."""
        # Placeholder - authorization logic TBD
        pass

    async def test_hr_can_access_any_review(self):
        """HR should be able to access any employee's review's goals."""
        # Placeholder - authorization logic TBD
        pass
