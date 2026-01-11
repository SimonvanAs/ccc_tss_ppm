# TSS PPM v3.0 - Team Repository Tests
"""Tests for team database repository."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.repositories.team import TeamRepository


class TestTeamRepository:
    """Tests for TeamRepository."""

    @pytest.fixture
    def mock_conn(self):
        """Create a mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    def team_repo(self, mock_conn):
        """Create a TeamRepository instance with mock connection."""
        return TeamRepository(mock_conn)

    @pytest.fixture
    def sample_team_member_row(self):
        """Sample team member data as returned from database."""
        return {
            'id': uuid4(),
            'email': 'employee@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'function_title': 'Software Engineer',
            'tov_level': 'B',
            'review_id': uuid4(),
            'review_stage': 'END_YEAR_REVIEW',
            'review_status': 'DRAFT',
            'goals_count': 3,
            'scored_goals_count': 0,
            'competency_scores_count': 0,
        }

    # --- get_team_members_by_manager_id tests ---

    async def test_get_team_members_returns_team(
        self, team_repo, mock_conn, sample_team_member_row
    ):
        """Should return list of team members for a manager."""
        manager_id = uuid4()
        mock_conn.fetch.return_value = [sample_team_member_row]

        team = await team_repo.get_team_members_by_manager_id(manager_id)

        assert len(team) == 1
        assert team[0]['email'] == 'employee@example.com'
        assert team[0]['first_name'] == 'John'
        mock_conn.fetch.assert_called_once()
        # Verify SQL contains manager_id filter
        call_args = mock_conn.fetch.call_args
        assert 'manager_id' in call_args[0][0].lower()

    async def test_get_team_members_empty(self, team_repo, mock_conn):
        """Should return empty list when manager has no team members."""
        manager_id = uuid4()
        mock_conn.fetch.return_value = []

        team = await team_repo.get_team_members_by_manager_id(manager_id)

        assert team == []

    async def test_get_team_members_with_review_year_filter(
        self, team_repo, mock_conn, sample_team_member_row
    ):
        """Should filter team members by review year."""
        manager_id = uuid4()
        mock_conn.fetch.return_value = [sample_team_member_row]

        await team_repo.get_team_members_by_manager_id(manager_id, review_year=2026)

        call_args = mock_conn.fetch.call_args
        assert 'review_year' in call_args[0][0].lower()
        # Second parameter should be the review year
        assert 2026 in call_args[0][1:]

    async def test_get_team_members_ordered_by_name(self, team_repo, mock_conn):
        """Team members should be ordered by last_name, first_name."""
        manager_id = uuid4()
        mock_conn.fetch.return_value = []

        await team_repo.get_team_members_by_manager_id(manager_id)

        call_args = mock_conn.fetch.call_args
        sql = call_args[0][0].lower()
        assert 'order by' in sql
        assert 'last_name' in sql or 'first_name' in sql

    # --- calculate_scoring_status tests ---

    def test_calculate_status_not_started(self, team_repo):
        """Should return NOT_STARTED when no goals are scored."""
        status = team_repo.calculate_scoring_status(
            goals_count=5, scored_goals_count=0, competency_scores_count=0
        )
        assert status == 'NOT_STARTED'

    def test_calculate_status_in_progress_partial_goals(self, team_repo):
        """Should return IN_PROGRESS when some goals are scored."""
        status = team_repo.calculate_scoring_status(
            goals_count=5, scored_goals_count=3, competency_scores_count=0
        )
        assert status == 'IN_PROGRESS'

    def test_calculate_status_in_progress_partial_competencies(self, team_repo):
        """Should return IN_PROGRESS when goals complete but competencies partial."""
        status = team_repo.calculate_scoring_status(
            goals_count=5,
            scored_goals_count=5,
            competency_scores_count=3,
            total_competencies=6,
        )
        assert status == 'IN_PROGRESS'

    def test_calculate_status_complete(self, team_repo):
        """Should return COMPLETE when all goals and competencies are scored."""
        status = team_repo.calculate_scoring_status(
            goals_count=5,
            scored_goals_count=5,
            competency_scores_count=6,
            total_competencies=6,
        )
        assert status == 'COMPLETE'

    def test_calculate_status_complete_no_goals(self, team_repo):
        """Should return COMPLETE when no goals exist and competencies scored."""
        status = team_repo.calculate_scoring_status(
            goals_count=0,
            scored_goals_count=0,
            competency_scores_count=6,
            total_competencies=6,
        )
        assert status == 'COMPLETE'

    def test_calculate_status_not_started_no_goals_or_competencies(self, team_repo):
        """Should return NOT_STARTED when nothing exists."""
        status = team_repo.calculate_scoring_status(
            goals_count=0, scored_goals_count=0, competency_scores_count=0
        )
        assert status == 'NOT_STARTED'

    # --- get_team_members_with_status tests ---

    async def test_get_team_members_with_status(
        self, team_repo, mock_conn, sample_team_member_row
    ):
        """Should return team members with calculated scoring status."""
        manager_id = uuid4()
        mock_conn.fetch.return_value = [sample_team_member_row]

        team = await team_repo.get_team_members_with_status(manager_id)

        assert len(team) == 1
        assert 'scoring_status' in team[0]
        # With 0 scored goals and 0 competency scores, status should be NOT_STARTED
        assert team[0]['scoring_status'] == 'NOT_STARTED'
