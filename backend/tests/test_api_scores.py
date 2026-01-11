# TSS PPM v3.0 - Scores API Tests
"""Tests for Scores API endpoints."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db


class TestScoresEndpoints:
    """Tests for GET and PUT /api/v1/reviews/{id}/scores endpoints."""

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
    def sample_goal_score(self):
        """Sample goal score data."""
        return {
            'id': uuid4(),
            'review_id': uuid4(),
            'title': 'Complete project',
            'description': 'Finish Q1 project',
            'goal_type': 'STANDARD',
            'weight': 25,
            'score': 2,
            'feedback': 'Good progress',
            'display_order': 0,
        }

    @pytest.fixture
    def sample_competency_score(self):
        """Sample competency score data."""
        return {
            'id': uuid4(),
            'review_id': uuid4(),
            'competency_id': uuid4(),
            'score': 3,
            'notes': 'Excellent performance',
            'category': 'Dedicated',
            'subcategory': 'Result driven',
            'title_en': 'Achieves Results',
            'display_order': 0,
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
    async def unauthenticated_client(self):
        """Async HTTP client without auth override."""
        app.dependency_overrides.clear()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    # --- GET /api/v1/reviews/{id}/scores tests ---

    async def test_get_scores_requires_auth(self, unauthenticated_client):
        """GET /reviews/:id/scores should require authentication."""
        review_id = uuid4()
        response = await unauthenticated_client.get(
            f'/api/v1/reviews/{review_id}/scores'
        )
        assert response.status_code in [401, 403]

    async def test_get_scores_returns_combined(
        self, manager_client, mock_db_conn, sample_goal_score, sample_competency_score
    ):
        """GET /reviews/:id/scores should return both goal and competency scores."""
        review_id = uuid4()
        # Mock both fetch calls (goal scores, then competency scores)
        mock_db_conn.fetch.side_effect = [
            [sample_goal_score],
            [sample_competency_score],
        ]

        response = await manager_client.get(f'/api/v1/reviews/{review_id}/scores')

        assert response.status_code == 200
        data = response.json()
        assert 'goal_scores' in data
        assert 'competency_scores' in data
        assert len(data['goal_scores']) == 1
        assert len(data['competency_scores']) == 1

    async def test_get_scores_empty(self, manager_client, mock_db_conn):
        """GET /reviews/:id/scores should return empty lists when no scores."""
        review_id = uuid4()
        mock_db_conn.fetch.side_effect = [[], []]

        response = await manager_client.get(f'/api/v1/reviews/{review_id}/scores')

        assert response.status_code == 200
        data = response.json()
        assert data['goal_scores'] == []
        assert data['competency_scores'] == []

    async def test_get_scores_goal_schema(
        self, manager_client, mock_db_conn, sample_goal_score
    ):
        """GET /reviews/:id/scores should return proper goal score schema."""
        review_id = uuid4()
        mock_db_conn.fetch.side_effect = [[sample_goal_score], []]

        response = await manager_client.get(f'/api/v1/reviews/{review_id}/scores')

        assert response.status_code == 200
        goal = response.json()['goal_scores'][0]
        assert 'id' in goal
        assert 'title' in goal
        assert 'score' in goal
        assert 'weight' in goal
        assert 'goal_type' in goal

    # --- PUT /api/v1/reviews/{id}/scores tests ---

    async def test_put_scores_requires_auth(self, unauthenticated_client):
        """PUT /reviews/:id/scores should require authentication."""
        review_id = uuid4()
        response = await unauthenticated_client.put(
            f'/api/v1/reviews/{review_id}/scores', json={'goal_scores': []}
        )
        assert response.status_code in [401, 403]

    async def test_put_scores_updates_goals(self, manager_client, mock_db_conn):
        """PUT /reviews/:id/scores should update goal scores."""
        review_id = uuid4()
        goal_id = uuid4()
        mock_db_conn.fetchrow.return_value = {
            'id': goal_id,
            'score': 3,
            'feedback': 'Updated',
        }

        response = await manager_client.put(
            f'/api/v1/reviews/{review_id}/scores',
            json={
                'goal_scores': [
                    {'goal_id': str(goal_id), 'score': 3, 'feedback': 'Updated'}
                ]
            },
        )

        assert response.status_code == 200
        assert mock_db_conn.fetchrow.called

    async def test_put_scores_updates_competencies(self, manager_client, mock_db_conn):
        """PUT /reviews/:id/scores should update competency scores."""
        review_id = uuid4()
        competency_id = uuid4()
        mock_db_conn.fetchrow.return_value = {
            'id': uuid4(),
            'score': 2,
            'notes': 'Good',
        }

        response = await manager_client.put(
            f'/api/v1/reviews/{review_id}/scores',
            json={
                'competency_scores': [
                    {'competency_id': str(competency_id), 'score': 2, 'notes': 'Good'}
                ]
            },
        )

        assert response.status_code == 200

    async def test_put_scores_validates_score_range(self, manager_client, mock_db_conn):
        """PUT /reviews/:id/scores should validate score range (1-3)."""
        review_id = uuid4()
        goal_id = uuid4()

        response = await manager_client.put(
            f'/api/v1/reviews/{review_id}/scores',
            json={'goal_scores': [{'goal_id': str(goal_id), 'score': 5}]},
        )

        # Should return validation error
        assert response.status_code == 422

    async def test_put_scores_partial_update(self, manager_client, mock_db_conn):
        """PUT /reviews/:id/scores should allow partial updates."""
        review_id = uuid4()
        goal_id = uuid4()
        mock_db_conn.fetchrow.return_value = {'id': goal_id, 'score': 2}

        response = await manager_client.put(
            f'/api/v1/reviews/{review_id}/scores',
            json={
                'goal_scores': [
                    {'goal_id': str(goal_id), 'score': 2}
                    # No feedback provided - should still work
                ]
            },
        )

        assert response.status_code == 200


class TestSubmitScoresEndpoint:
    """Tests for POST /api/v1/reviews/{id}/submit-scores endpoint."""

    @pytest.fixture
    def mock_manager_user(self):
        """Mock authenticated manager user."""
        return CurrentUser(
            keycloak_id='test-manager-keycloak-id',
            email='manager@example.com',
            name='Test Manager',
            roles=['employee', 'manager'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_employee_user(self):
        """Mock authenticated employee user (not a manager)."""
        return CurrentUser(
            keycloak_id='test-employee-keycloak-id',
            email='employee@example.com',
            name='Test Employee',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    def sample_review_draft(self):
        """Sample review in DRAFT status."""
        return {
            'id': uuid4(),
            'employee_id': uuid4(),
            'manager_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'what_score': None,
            'how_score': None,
            'opco_id': uuid4(),
        }

    @pytest.fixture
    def sample_goals_all_scored(self):
        """Sample goals all with scores."""
        return [
            {'id': uuid4(), 'score': 2, 'weight': 40, 'goal_type': 'STANDARD'},
            {'id': uuid4(), 'score': 3, 'weight': 30, 'goal_type': 'KAR'},
            {'id': uuid4(), 'score': 2, 'weight': 30, 'goal_type': 'SCF'},
        ]

    @pytest.fixture
    def sample_competency_scores_all(self):
        """Sample competency scores - all 6 required."""
        return [
            {'competency_id': uuid4(), 'score': 2},
            {'competency_id': uuid4(), 'score': 2},
            {'competency_id': uuid4(), 'score': 3},
            {'competency_id': uuid4(), 'score': 2},
            {'competency_id': uuid4(), 'score': 2},
            {'competency_id': uuid4(), 'score': 3},
        ]

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
        """Async HTTP client with employee (non-manager) authentication."""
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

    # --- Authentication Tests ---

    async def test_submit_scores_requires_auth(self, unauthenticated_client):
        """POST /reviews/:id/submit-scores should require authentication."""
        review_id = uuid4()
        response = await unauthenticated_client.post(
            f'/api/v1/reviews/{review_id}/submit-scores'
        )
        assert response.status_code in [401, 403]

    async def test_submit_scores_requires_manager_role(
        self, employee_client, mock_db_conn
    ):
        """POST /reviews/:id/submit-scores should require manager role."""
        review_id = uuid4()
        response = await employee_client.post(
            f'/api/v1/reviews/{review_id}/submit-scores'
        )
        assert response.status_code == 403
        assert 'manager' in response.json()['detail'].lower()

    # --- Authorization Tests ---

    async def test_submit_scores_only_review_manager_can_submit(
        self, manager_client, mock_db_conn, mock_manager_user
    ):
        """Only the manager of the review can submit scores."""
        review_id = uuid4()
        other_manager_id = uuid4()

        mock_db_conn.fetchrow.side_effect = [
            {'id': uuid4()},  # Current user's internal ID
            {
                'id': review_id,
                'employee_id': uuid4(),
                'manager_id': other_manager_id,
                'status': 'DRAFT',
                'stage': 'END_YEAR_REVIEW',
                'review_year': 2026,
            },
        ]

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/submit-scores'
        )

        assert response.status_code == 403
        assert 'not authorized' in response.json()['detail'].lower()

    # --- Status Transition Tests ---

    async def test_submit_scores_transitions_draft_to_pending(
        self,
        manager_client,
        mock_db_conn,
        mock_manager_user,
        sample_goals_all_scored,
        sample_competency_scores_all,
    ):
        """Submit scores should transition DRAFT → PENDING_EMPLOYEE_SIGNATURE."""
        review_id = uuid4()
        user_id = uuid4()

        mock_db_conn.fetchrow.side_effect = [
            {'id': user_id},
            {
                'id': review_id,
                'employee_id': uuid4(),
                'manager_id': user_id,
                'status': 'DRAFT',
                'stage': 'END_YEAR_REVIEW',
                'review_year': 2026,
                'opco_id': uuid4(),
            },
            {
                'id': review_id,
                'status': 'PENDING_EMPLOYEE_SIGNATURE',
            },
            {'id': uuid4()},
        ]

        mock_db_conn.fetch.side_effect = [
            sample_goals_all_scored,
            sample_competency_scores_all,
        ]

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/submit-scores'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'PENDING_EMPLOYEE_SIGNATURE'

    async def test_submit_scores_rejects_non_draft_status(
        self, manager_client, mock_db_conn, mock_manager_user
    ):
        """Submit scores should reject if review not in DRAFT status."""
        review_id = uuid4()
        user_id = uuid4()

        mock_db_conn.fetchrow.side_effect = [
            {'id': user_id},
            {
                'id': review_id,
                'employee_id': uuid4(),
                'manager_id': user_id,
                'status': 'PENDING_EMPLOYEE_SIGNATURE',
                'stage': 'END_YEAR_REVIEW',
                'review_year': 2026,
            },
        ]

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/submit-scores'
        )

        assert response.status_code == 400
        assert 'DRAFT' in response.json()['detail']

    # --- Validation Tests ---

    async def test_submit_scores_requires_all_goals_scored(
        self, manager_client, mock_db_conn, mock_manager_user
    ):
        """Submit scores should require all goals to have scores."""
        review_id = uuid4()
        user_id = uuid4()

        mock_db_conn.fetchrow.side_effect = [
            {'id': user_id},
            {
                'id': review_id,
                'employee_id': uuid4(),
                'manager_id': user_id,
                'status': 'DRAFT',
                'stage': 'END_YEAR_REVIEW',
                'review_year': 2026,
            },
        ]

        mock_db_conn.fetch.side_effect = [
            [
                {'id': uuid4(), 'score': 2, 'weight': 50, 'goal_type': 'STANDARD'},
                {'id': uuid4(), 'score': None, 'weight': 50, 'goal_type': 'KAR'},
            ],
            [],
        ]

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/submit-scores'
        )

        assert response.status_code == 400
        assert 'goal' in response.json()['detail'].lower()

    async def test_submit_scores_requires_all_competencies_scored(
        self,
        manager_client,
        mock_db_conn,
        mock_manager_user,
        sample_goals_all_scored,
    ):
        """Submit scores should require all 6 competencies to have scores."""
        review_id = uuid4()
        user_id = uuid4()

        mock_db_conn.fetchrow.side_effect = [
            {'id': user_id},
            {
                'id': review_id,
                'employee_id': uuid4(),
                'manager_id': user_id,
                'status': 'DRAFT',
                'stage': 'END_YEAR_REVIEW',
                'review_year': 2026,
            },
        ]

        mock_db_conn.fetch.side_effect = [
            sample_goals_all_scored,
            [
                {'competency_id': uuid4(), 'score': 2},
                {'competency_id': uuid4(), 'score': 2},
                {'competency_id': uuid4(), 'score': 3},
                {'competency_id': uuid4(), 'score': 2},
            ],
        ]

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/submit-scores'
        )

        assert response.status_code == 400
        assert 'competenc' in response.json()['detail'].lower()

    # --- Idempotency Tests ---

    async def test_submit_scores_idempotent_already_submitted(
        self, manager_client, mock_db_conn, mock_manager_user
    ):
        """Submitting already submitted review should return 400."""
        review_id = uuid4()
        user_id = uuid4()

        mock_db_conn.fetchrow.side_effect = [
            {'id': user_id},
            {
                'id': review_id,
                'employee_id': uuid4(),
                'manager_id': user_id,
                'status': 'EMPLOYEE_SIGNED',
                'stage': 'END_YEAR_REVIEW',
                'review_year': 2026,
            },
        ]

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/submit-scores'
        )

        assert response.status_code == 400
        assert 'DRAFT' in response.json()['detail']

    # --- Not Found Tests ---

    async def test_submit_scores_review_not_found(
        self, manager_client, mock_db_conn, mock_manager_user
    ):
        """Submit scores should return 404 if review doesn't exist."""
        review_id = uuid4()

        mock_db_conn.fetchrow.side_effect = [
            {'id': uuid4()},
            None,
        ]

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/submit-scores'
        )

        assert response.status_code == 404
        assert 'not found' in response.json()['detail'].lower()
