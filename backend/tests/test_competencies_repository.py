# TSS PPM v3.0 - Competencies Repository Tests
"""Tests for competencies database repository."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.repositories.competencies import CompetenciesRepository


class TestCompetenciesRepository:
    """Tests for CompetenciesRepository."""

    @pytest.fixture
    def mock_conn(self):
        """Create a mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    def repo(self, mock_conn):
        """Create a CompetenciesRepository instance with mock connection."""
        return CompetenciesRepository(mock_conn)

    @pytest.fixture
    def sample_competency_row(self):
        """Sample competency data as returned from database."""
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

    # --- get_competencies_by_level tests ---

    async def test_get_competencies_returns_list(
        self, repo, mock_conn, sample_competency_row
    ):
        """Should return list of competencies for a TOV level."""
        mock_conn.fetch.return_value = [sample_competency_row]

        competencies = await repo.get_competencies_by_level('B')

        assert len(competencies) == 1
        assert competencies[0]['category'] == 'Dedicated'
        assert competencies[0]['title_en'] == 'Achieves Results'
        mock_conn.fetch.assert_called_once()

    async def test_get_competencies_filters_by_level(
        self, repo, mock_conn, sample_competency_row
    ):
        """Should filter competencies by TOV level."""
        mock_conn.fetch.return_value = [sample_competency_row]

        await repo.get_competencies_by_level('B')

        call_args = mock_conn.fetch.call_args
        sql = call_args[0][0].lower()
        assert 'level = $1' in sql or 'level =' in sql
        assert 'B' in call_args[0][1:]

    async def test_get_competencies_empty(self, repo, mock_conn):
        """Should return empty list when no competencies exist for level."""
        mock_conn.fetch.return_value = []

        competencies = await repo.get_competencies_by_level('X')

        assert competencies == []

    async def test_get_competencies_with_opco_filter(
        self, repo, mock_conn, sample_competency_row
    ):
        """Should filter competencies by opco_id when provided."""
        opco_id = uuid4()
        mock_conn.fetch.return_value = [sample_competency_row]

        await repo.get_competencies_by_level('B', opco_id=opco_id)

        call_args = mock_conn.fetch.call_args
        sql = call_args[0][0].lower()
        assert 'opco_id' in sql
        assert opco_id in call_args[0][1:]

    async def test_get_competencies_ordered_by_category(self, repo, mock_conn):
        """Should order competencies by category and display_order."""
        mock_conn.fetch.return_value = []

        await repo.get_competencies_by_level('B')

        call_args = mock_conn.fetch.call_args
        sql = call_args[0][0].lower()
        assert 'order by' in sql
        assert 'category' in sql
        assert 'display_order' in sql

    async def test_get_competencies_returns_all_levels(
        self, repo, mock_conn, sample_competency_row
    ):
        """Should work for all valid TOV levels."""
        mock_conn.fetch.return_value = [sample_competency_row]

        for level in ['A', 'B', 'C', 'D']:
            competencies = await repo.get_competencies_by_level(level)
            assert isinstance(competencies, list)

    async def test_get_competencies_returns_dict(
        self, repo, mock_conn, sample_competency_row
    ):
        """Should return list of dictionaries."""
        mock_conn.fetch.return_value = [sample_competency_row]

        competencies = await repo.get_competencies_by_level('B')

        assert isinstance(competencies[0], dict)
        assert 'id' in competencies[0]
        assert 'level' in competencies[0]
        assert 'category' in competencies[0]
