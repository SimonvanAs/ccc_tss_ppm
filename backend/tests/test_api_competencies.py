# TSS PPM v3.0 - Competencies API Tests
"""Tests for Competencies API endpoints."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db


class TestCompetenciesEndpoint:
    """Tests for GET /api/v1/competencies endpoint."""

    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user."""
        return CurrentUser(
            keycloak_id='test-user-id',
            email='user@example.com',
            name='Test User',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def sample_competency(self):
        """Sample competency data."""
        return {
            'id': uuid4(),
            'level': 'B',
            'category': 'Dedicated',
            'subcategory': 'Result driven',
            'title_en': 'Achieves Results',
            'title_nl': 'Behaalt Resultaten',
            'title_es': 'Logra Resultados',
            'indicators_en': ['Meets deadlines', 'Delivers quality'],
            'display_order': 0,
        }

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    async def client(self, mock_user, mock_db_conn):
        """Async HTTP client with authentication."""
        app.dependency_overrides[get_current_user] = lambda: mock_user
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

    # --- GET /api/v1/competencies tests ---

    async def test_get_competencies_requires_auth(self, unauthenticated_client):
        """GET /competencies should require authentication."""
        response = await unauthenticated_client.get('/api/v1/competencies?tov_level=B')
        assert response.status_code in [401, 403]

    async def test_get_competencies_requires_tov_level(self, client):
        """GET /competencies should require tov_level query parameter."""
        response = await client.get('/api/v1/competencies')
        assert response.status_code == 422  # Validation error

    async def test_get_competencies_returns_list(
        self, client, mock_db_conn, sample_competency
    ):
        """GET /competencies should return list of competencies."""
        mock_db_conn.fetch.return_value = [sample_competency]

        response = await client.get('/api/v1/competencies?tov_level=B')

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['category'] == 'Dedicated'
        assert data[0]['title_en'] == 'Achieves Results'

    async def test_get_competencies_empty(self, client, mock_db_conn):
        """GET /competencies should return empty list for unknown TOV level."""
        mock_db_conn.fetch.return_value = []

        response = await client.get('/api/v1/competencies?tov_level=X')

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_get_competencies_validates_tov_level(self, client, mock_db_conn):
        """GET /competencies should validate tov_level is A, B, C, or D."""
        mock_db_conn.fetch.return_value = []

        # Valid levels should work
        for level in ['A', 'B', 'C', 'D']:
            response = await client.get(f'/api/v1/competencies?tov_level={level}')
            assert response.status_code == 200

    async def test_get_competencies_filters_by_level(
        self, client, mock_db_conn, sample_competency
    ):
        """GET /competencies should filter by TOV level."""
        mock_db_conn.fetch.return_value = [sample_competency]

        await client.get('/api/v1/competencies?tov_level=B')

        # Verify the query was called with level parameter
        call_args = mock_db_conn.fetch.call_args
        assert 'B' in call_args[0][1:]

    async def test_get_competencies_ordered_by_category(
        self, client, mock_db_conn, sample_competency
    ):
        """GET /competencies should be ordered by category and display_order."""
        mock_db_conn.fetch.return_value = [sample_competency]

        await client.get('/api/v1/competencies?tov_level=B')

        call_args = mock_db_conn.fetch.call_args
        sql = call_args[0][0].lower()
        assert 'order by' in sql

    async def test_get_competencies_response_schema(
        self, client, mock_db_conn, sample_competency
    ):
        """GET /competencies should return proper response schema."""
        mock_db_conn.fetch.return_value = [sample_competency]

        response = await client.get('/api/v1/competencies?tov_level=B')

        assert response.status_code == 200
        comp = response.json()[0]

        # Verify expected fields
        expected_fields = [
            'id',
            'level',
            'category',
            'subcategory',
            'title_en',
            'display_order',
        ]
        for field in expected_fields:
            assert field in comp, f'Field {field} missing from response'
