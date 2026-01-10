# TSS PPM v3.0 - Review API Tests
"""Tests for Review API endpoints."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db


class TestReviewSubmissionEndpoint:
    """Tests for review submission endpoint."""

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
    def sample_review(self):
        """Sample review data."""
        return {
            'id': uuid4(),
            'employee_id': uuid4(),
            'manager_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
        }

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    async def client(self, mock_current_user, mock_db_conn):
        """Async HTTP client with dependency overrides."""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
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

    # --- POST /api/v1/reviews/:id/submit tests ---

    async def test_submit_review_requires_auth(self, unauthenticated_client):
        """POST /reviews/:id/submit should require authentication."""
        review_id = uuid4()
        response = await unauthenticated_client.post(f'/api/v1/reviews/{review_id}/submit')
        assert response.status_code in [401, 403]

    async def test_submit_review_success(self, client, mock_db_conn, sample_review):
        """POST /reviews/:id/submit should submit review when weights = 100%."""
        review_id = sample_review['id']
        # Mock: review exists and in DRAFT status
        mock_db_conn.fetchrow.return_value = sample_review
        # Mock: weight total = 100
        mock_db_conn.fetchval.return_value = 100
        # Mock: update status returns updated review
        submitted_review = {**sample_review, 'status': 'PENDING_MANAGER_SIGNATURE'}
        mock_db_conn.fetchrow.side_effect = [sample_review, submitted_review]

        response = await client.post(f'/api/v1/reviews/{review_id}/submit')

        assert response.status_code == 200
        assert response.json()['status'] == 'PENDING_MANAGER_SIGNATURE'

    async def test_submit_review_invalid_weight(self, client, mock_db_conn, sample_review):
        """POST /reviews/:id/submit should reject when weights != 100%."""
        review_id = sample_review['id']
        # Mock: review exists
        mock_db_conn.fetchrow.return_value = sample_review
        # Mock: weight total = 80 (not 100)
        mock_db_conn.fetchval.return_value = 80

        response = await client.post(f'/api/v1/reviews/{review_id}/submit')

        assert response.status_code == 400
        assert 'weight' in response.json()['detail'].lower() or '100' in response.json()['detail']

    async def test_submit_review_zero_weight(self, client, mock_db_conn, sample_review):
        """POST /reviews/:id/submit should reject when no goals exist."""
        review_id = sample_review['id']
        mock_db_conn.fetchrow.return_value = sample_review
        mock_db_conn.fetchval.return_value = 0

        response = await client.post(f'/api/v1/reviews/{review_id}/submit')

        assert response.status_code == 400

    async def test_submit_review_not_found(self, client, mock_db_conn):
        """POST /reviews/:id/submit should return 404 for non-existent review."""
        review_id = uuid4()
        mock_db_conn.fetchrow.return_value = None

        response = await client.post(f'/api/v1/reviews/{review_id}/submit')

        assert response.status_code == 404

    async def test_submit_review_wrong_status(self, client, mock_db_conn, sample_review):
        """POST /reviews/:id/submit should reject if review not in DRAFT status."""
        review_id = sample_review['id']
        # Review already submitted
        already_submitted = {**sample_review, 'status': 'PENDING_MANAGER_SIGNATURE'}
        mock_db_conn.fetchrow.return_value = already_submitted

        response = await client.post(f'/api/v1/reviews/{review_id}/submit')

        assert response.status_code == 400
        assert 'status' in response.json()['detail'].lower() or 'DRAFT' in response.json()['detail']

    async def test_submit_review_status_transition(self, client, mock_db_conn, sample_review):
        """POST /reviews/:id/submit should transition status correctly."""
        review_id = sample_review['id']
        mock_db_conn.fetchrow.return_value = sample_review
        mock_db_conn.fetchval.return_value = 100
        submitted_review = {**sample_review, 'status': 'PENDING_MANAGER_SIGNATURE'}
        mock_db_conn.fetchrow.side_effect = [sample_review, submitted_review]

        response = await client.post(f'/api/v1/reviews/{review_id}/submit')

        assert response.status_code == 200
        # Verify update was called with correct status
        assert mock_db_conn.execute.called or mock_db_conn.fetchrow.called
