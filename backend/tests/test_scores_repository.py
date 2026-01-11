# TSS PPM v3.0 - Scores Repository Tests
"""Tests for scores database repository."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.repositories.scores import ScoresRepository


class TestScoresRepository:
    """Tests for ScoresRepository."""

    @pytest.fixture
    def mock_conn(self):
        """Create a mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    def scores_repo(self, mock_conn):
        """Create a ScoresRepository instance with mock connection."""
        return ScoresRepository(mock_conn)

    @pytest.fixture
    def sample_goal_score_row(self):
        """Sample goal score data as returned from database."""
        return {
            'id': uuid4(),
            'review_id': uuid4(),
            'title': 'Complete project',
            'description': 'Finish the annual project',
            'goal_type': 'STANDARD',
            'weight': 25,
            'score': 2,
            'feedback': 'Good progress on this goal',
            'display_order': 0,
        }

    @pytest.fixture
    def sample_competency_score_row(self):
        """Sample competency score data as returned from database."""
        return {
            'id': uuid4(),
            'review_id': uuid4(),
            'competency_id': uuid4(),
            'score': 3,
            'notes': 'Excellent demonstration of this competency',
            'category': 'Dedicated',
            'subcategory': 'Result driven',
            'title_en': 'Achieves Results',
        }

    # --- get_goal_scores tests ---

    async def test_get_goal_scores_returns_scores(
        self, scores_repo, mock_conn, sample_goal_score_row
    ):
        """Should return list of goal scores for a review."""
        review_id = uuid4()
        mock_conn.fetch.return_value = [sample_goal_score_row]

        scores = await scores_repo.get_goal_scores(review_id)

        assert len(scores) == 1
        assert scores[0]['score'] == 2
        assert scores[0]['title'] == 'Complete project'
        mock_conn.fetch.assert_called_once()

    async def test_get_goal_scores_empty(self, scores_repo, mock_conn):
        """Should return empty list when no goals exist."""
        review_id = uuid4()
        mock_conn.fetch.return_value = []

        scores = await scores_repo.get_goal_scores(review_id)

        assert scores == []

    async def test_get_goal_scores_ordered_by_display_order(
        self, scores_repo, mock_conn
    ):
        """Goals should be ordered by display_order."""
        review_id = uuid4()
        mock_conn.fetch.return_value = []

        await scores_repo.get_goal_scores(review_id)

        call_args = mock_conn.fetch.call_args
        assert 'display_order' in call_args[0][0].lower()

    # --- get_competency_scores tests ---

    async def test_get_competency_scores_returns_scores(
        self, scores_repo, mock_conn, sample_competency_score_row
    ):
        """Should return list of competency scores for a review."""
        review_id = uuid4()
        mock_conn.fetch.return_value = [sample_competency_score_row]

        scores = await scores_repo.get_competency_scores(review_id)

        assert len(scores) == 1
        assert scores[0]['score'] == 3
        assert scores[0]['category'] == 'Dedicated'
        mock_conn.fetch.assert_called_once()

    async def test_get_competency_scores_empty(self, scores_repo, mock_conn):
        """Should return empty list when no competency scores exist."""
        review_id = uuid4()
        mock_conn.fetch.return_value = []

        scores = await scores_repo.get_competency_scores(review_id)

        assert scores == []

    async def test_get_competency_scores_includes_competency_info(
        self, scores_repo, mock_conn, sample_competency_score_row
    ):
        """Should include competency metadata (category, title)."""
        review_id = uuid4()
        mock_conn.fetch.return_value = [sample_competency_score_row]

        await scores_repo.get_competency_scores(review_id)

        call_args = mock_conn.fetch.call_args
        sql = call_args[0][0].lower()
        # Should join with competencies table
        assert 'competencies' in sql or 'join' in sql

    # --- get_all_scores tests ---

    async def test_get_all_scores_returns_combined(
        self, scores_repo, mock_conn, sample_goal_score_row, sample_competency_score_row
    ):
        """Should return both goal and competency scores."""
        review_id = uuid4()
        # Mock both fetch calls
        mock_conn.fetch.side_effect = [
            [sample_goal_score_row],
            [sample_competency_score_row],
        ]

        result = await scores_repo.get_all_scores(review_id)

        assert 'goal_scores' in result
        assert 'competency_scores' in result
        assert len(result['goal_scores']) == 1
        assert len(result['competency_scores']) == 1

    # --- upsert_goal_score tests ---

    async def test_upsert_goal_score_update(
        self, scores_repo, mock_conn, sample_goal_score_row
    ):
        """Should update existing goal score."""
        goal_id = uuid4()
        mock_conn.fetchrow.return_value = sample_goal_score_row

        result = await scores_repo.upsert_goal_score(
            goal_id=goal_id, score=3, feedback='Updated feedback'
        )

        assert result is not None
        mock_conn.fetchrow.assert_called_once()
        call_args = mock_conn.fetchrow.call_args
        assert 'update' in call_args[0][0].lower()

    async def test_upsert_goal_score_with_feedback(
        self, scores_repo, mock_conn, sample_goal_score_row
    ):
        """Should save feedback along with score."""
        goal_id = uuid4()
        feedback = 'Great work on this goal'
        mock_conn.fetchrow.return_value = sample_goal_score_row

        await scores_repo.upsert_goal_score(
            goal_id=goal_id, score=2, feedback=feedback
        )

        call_args = mock_conn.fetchrow.call_args
        assert feedback in call_args[0][1:]

    async def test_upsert_goal_score_validates_range(self, scores_repo, mock_conn):
        """Should validate score is between 1 and 3."""
        goal_id = uuid4()

        with pytest.raises(ValueError):
            await scores_repo.upsert_goal_score(goal_id=goal_id, score=0)

        with pytest.raises(ValueError):
            await scores_repo.upsert_goal_score(goal_id=goal_id, score=4)

    # --- upsert_competency_score tests ---

    async def test_upsert_competency_score_insert(
        self, scores_repo, mock_conn, sample_competency_score_row
    ):
        """Should insert new competency score."""
        review_id = uuid4()
        competency_id = uuid4()
        mock_conn.fetchrow.return_value = sample_competency_score_row

        result = await scores_repo.upsert_competency_score(
            review_id=review_id, competency_id=competency_id, score=2
        )

        assert result is not None
        mock_conn.fetchrow.assert_called_once()

    async def test_upsert_competency_score_with_notes(
        self, scores_repo, mock_conn, sample_competency_score_row
    ):
        """Should save notes along with score."""
        review_id = uuid4()
        competency_id = uuid4()
        notes = 'Demonstrated excellent leadership'
        mock_conn.fetchrow.return_value = sample_competency_score_row

        await scores_repo.upsert_competency_score(
            review_id=review_id,
            competency_id=competency_id,
            score=3,
            notes=notes,
        )

        call_args = mock_conn.fetchrow.call_args
        assert notes in call_args[0][1:]

    async def test_upsert_competency_score_validates_range(
        self, scores_repo, mock_conn
    ):
        """Should validate score is between 1 and 3."""
        review_id = uuid4()
        competency_id = uuid4()

        with pytest.raises(ValueError):
            await scores_repo.upsert_competency_score(
                review_id=review_id, competency_id=competency_id, score=0
            )

        with pytest.raises(ValueError):
            await scores_repo.upsert_competency_score(
                review_id=review_id, competency_id=competency_id, score=4
            )

    # --- bulk_upsert_scores tests ---

    async def test_bulk_upsert_goal_scores(self, scores_repo, mock_conn):
        """Should update multiple goal scores at once."""
        goal_scores = [
            {'goal_id': uuid4(), 'score': 2, 'feedback': 'Good'},
            {'goal_id': uuid4(), 'score': 3, 'feedback': 'Excellent'},
        ]
        mock_conn.fetchrow.return_value = {'id': uuid4(), 'score': 2}

        await scores_repo.bulk_upsert_goal_scores(goal_scores)

        assert mock_conn.fetchrow.call_count == 2

    async def test_bulk_upsert_competency_scores(self, scores_repo, mock_conn):
        """Should update multiple competency scores at once."""
        review_id = uuid4()
        competency_scores = [
            {'competency_id': uuid4(), 'score': 2},
            {'competency_id': uuid4(), 'score': 3},
        ]
        mock_conn.fetchrow.return_value = {'id': uuid4(), 'score': 2}

        await scores_repo.bulk_upsert_competency_scores(review_id, competency_scores)

        assert mock_conn.fetchrow.call_count == 2

    # --- Review HOW Score Persistence Tests ---

    async def test_update_review_how_score(self, scores_repo, mock_conn):
        """Should update review how_score field."""
        review_id = uuid4()
        how_score = 2.50
        mock_conn.fetchrow.return_value = {
            'id': review_id,
            'how_score': how_score,
            'how_veto_active': False,
            'grid_position_how': 3,
        }

        result = await scores_repo.update_review_how_score(
            review_id=review_id,
            how_score=how_score,
            how_veto_active=False,
            grid_position_how=3,
        )

        assert result['how_score'] == how_score
        mock_conn.fetchrow.assert_called_once()

    async def test_update_review_how_score_with_veto(self, scores_repo, mock_conn):
        """Should update review with VETO flag when any score is 1."""
        review_id = uuid4()
        mock_conn.fetchrow.return_value = {
            'id': review_id,
            'how_score': 1.00,
            'how_veto_active': True,
            'grid_position_how': 1,
        }

        result = await scores_repo.update_review_how_score(
            review_id=review_id,
            how_score=1.00,
            how_veto_active=True,
            grid_position_how=1,
        )

        assert result['how_veto_active'] is True
        assert result['how_score'] == 1.00

    async def test_update_review_grid_position_how(self, scores_repo, mock_conn):
        """Should update review grid_position_how field."""
        review_id = uuid4()
        mock_conn.fetchrow.return_value = {
            'id': review_id,
            'how_score': 2.00,
            'how_veto_active': False,
            'grid_position_how': 2,
        }

        result = await scores_repo.update_review_how_score(
            review_id=review_id,
            how_score=2.00,
            how_veto_active=False,
            grid_position_how=2,
        )

        assert result['grid_position_how'] == 2

    async def test_recalculate_and_update_how_score(self, scores_repo, mock_conn):
        """Should recalculate HOW score from competency scores and update review."""
        review_id = uuid4()
        # Mock competency scores fetch - 6 scores averaging to 2.50
        mock_conn.fetch.return_value = [
            {'score': 2}, {'score': 3}, {'score': 2},
            {'score': 3}, {'score': 2}, {'score': 3},
        ]
        mock_conn.fetchrow.return_value = {
            'id': review_id,
            'how_score': 2.50,
            'how_veto_active': False,
            'grid_position_how': 3,
        }

        result = await scores_repo.recalculate_and_update_how_score(review_id)

        assert result['how_score'] == 2.50
        assert result['how_veto_active'] is False
        assert result['grid_position_how'] == 3

    async def test_recalculate_with_veto_triggered(self, scores_repo, mock_conn):
        """Should set HOW score to 1.00 when VETO is triggered."""
        review_id = uuid4()
        # Mock competency scores with one score = 1 (triggers VETO)
        mock_conn.fetch.return_value = [
            {'score': 1}, {'score': 3}, {'score': 2},
            {'score': 3}, {'score': 2}, {'score': 3},
        ]
        mock_conn.fetchrow.return_value = {
            'id': review_id,
            'how_score': 1.00,
            'how_veto_active': True,
            'grid_position_how': 1,
        }

        result = await scores_repo.recalculate_and_update_how_score(review_id)

        assert result['how_score'] == 1.00
        assert result['how_veto_active'] is True
        assert result['grid_position_how'] == 1

    async def test_recalculate_with_incomplete_scores(self, scores_repo, mock_conn):
        """Should return None when fewer than 6 competency scores exist."""
        review_id = uuid4()
        # Mock only 3 competency scores
        mock_conn.fetch.return_value = [
            {'score': 2}, {'score': 3}, {'score': 2},
        ]

        result = await scores_repo.recalculate_and_update_how_score(review_id)

        # Should not update review when incomplete
        assert result is None
        mock_conn.fetchrow.assert_not_called()
