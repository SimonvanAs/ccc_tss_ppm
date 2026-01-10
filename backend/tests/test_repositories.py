# TSS PPM v3.0 - Repository Tests
"""Tests for database repositories."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.repositories.goals import GoalRepository
from src.schemas.goal import GoalCreate, GoalType


class TestGoalRepository:
    """Tests for GoalRepository."""

    @pytest.fixture
    def mock_conn(self):
        """Create a mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    def goal_repo(self, mock_conn):
        """Create a GoalRepository instance with mock connection."""
        return GoalRepository(mock_conn)

    @pytest.fixture
    def sample_goal_row(self):
        """Sample goal data as returned from database."""
        return {
            'id': uuid4(),
            'review_id': uuid4(),
            'title': 'Complete project',
            'description': 'Finish the annual project',
            'goal_type': 'STANDARD',
            'weight': 25,
            'score': None,
            'display_order': 0,
        }

    # --- get_goals_by_review tests ---

    async def test_get_goals_by_review_returns_goals(self, goal_repo, mock_conn, sample_goal_row):
        """Should return list of goals for a review."""
        review_id = uuid4()
        mock_conn.fetch.return_value = [sample_goal_row]

        goals = await goal_repo.get_goals_by_review(review_id)

        assert len(goals) == 1
        assert goals[0]['title'] == 'Complete project'
        mock_conn.fetch.assert_called_once()
        # Verify SQL contains review_id filter
        call_args = mock_conn.fetch.call_args
        assert 'review_id' in call_args[0][0].lower()

    async def test_get_goals_by_review_empty(self, goal_repo, mock_conn):
        """Should return empty list when no goals exist."""
        review_id = uuid4()
        mock_conn.fetch.return_value = []

        goals = await goal_repo.get_goals_by_review(review_id)

        assert goals == []

    async def test_get_goals_by_review_ordered_by_display_order(self, goal_repo, mock_conn):
        """Goals should be ordered by display_order."""
        review_id = uuid4()
        mock_conn.fetch.return_value = []

        await goal_repo.get_goals_by_review(review_id)

        call_args = mock_conn.fetch.call_args
        assert 'display_order' in call_args[0][0].lower()

    # --- get_goal tests ---

    async def test_get_goal_returns_goal(self, goal_repo, mock_conn, sample_goal_row):
        """Should return a single goal by ID."""
        goal_id = uuid4()
        mock_conn.fetchrow.return_value = sample_goal_row

        goal = await goal_repo.get_goal(goal_id)

        assert goal is not None
        assert goal['title'] == 'Complete project'
        mock_conn.fetchrow.assert_called_once()

    async def test_get_goal_not_found(self, goal_repo, mock_conn):
        """Should return None when goal doesn't exist."""
        goal_id = uuid4()
        mock_conn.fetchrow.return_value = None

        goal = await goal_repo.get_goal(goal_id)

        assert goal is None

    # --- create_goal tests ---

    async def test_create_goal_success(self, goal_repo, mock_conn, sample_goal_row):
        """Should create a new goal and return it."""
        review_id = uuid4()
        goal_data = GoalCreate(
            title='New goal',
            description='Description',
            goal_type=GoalType.STANDARD,
            weight=20,
        )
        mock_conn.fetchrow.return_value = sample_goal_row

        goal = await goal_repo.create_goal(review_id, goal_data)

        assert goal is not None
        mock_conn.fetchrow.assert_called_once()
        call_args = mock_conn.fetchrow.call_args
        assert 'insert' in call_args[0][0].lower()

    async def test_create_goal_with_kar_type(self, goal_repo, mock_conn, sample_goal_row):
        """Should create goal with KAR type."""
        review_id = uuid4()
        goal_data = GoalCreate(
            title='KAR goal',
            goal_type=GoalType.KAR,
            weight=30,
        )
        mock_conn.fetchrow.return_value = sample_goal_row

        await goal_repo.create_goal(review_id, goal_data)

        call_args = mock_conn.fetchrow.call_args
        # Verify KAR type is passed to query
        assert 'KAR' in str(call_args)

    async def test_create_goal_sets_display_order(self, goal_repo, mock_conn, sample_goal_row):
        """Should set display_order based on existing goals count."""
        review_id = uuid4()
        goal_data = GoalCreate(title='Test', weight=10)
        mock_conn.fetchrow.return_value = sample_goal_row
        mock_conn.fetchval.return_value = 3  # 3 existing goals

        await goal_repo.create_goal(review_id, goal_data)

        # Verify display_order query was called
        calls = [str(c) for c in mock_conn.fetchval.call_args_list]
        assert any('count' in c.lower() or 'display_order' in c.lower() for c in calls)

    # --- update_goal tests ---

    async def test_update_goal_success(self, goal_repo, mock_conn, sample_goal_row):
        """Should update an existing goal."""
        goal_id = uuid4()
        updates = {'title': 'Updated title', 'weight': 30}
        mock_conn.fetchrow.return_value = sample_goal_row

        goal = await goal_repo.update_goal(goal_id, updates)

        assert goal is not None
        mock_conn.fetchrow.assert_called_once()
        call_args = mock_conn.fetchrow.call_args
        assert 'update' in call_args[0][0].lower()

    async def test_update_goal_partial(self, goal_repo, mock_conn, sample_goal_row):
        """Should allow partial updates."""
        goal_id = uuid4()
        updates = {'weight': 50}  # Only update weight
        mock_conn.fetchrow.return_value = sample_goal_row

        await goal_repo.update_goal(goal_id, updates)

        call_args = mock_conn.fetchrow.call_args
        assert 'weight' in call_args[0][0].lower()

    async def test_update_goal_not_found(self, goal_repo, mock_conn):
        """Should return None when goal doesn't exist."""
        goal_id = uuid4()
        updates = {'title': 'Updated'}
        mock_conn.fetchrow.return_value = None

        goal = await goal_repo.update_goal(goal_id, updates)

        assert goal is None

    # --- delete_goal tests ---

    async def test_delete_goal_success(self, goal_repo, mock_conn):
        """Should delete a goal (soft delete)."""
        goal_id = uuid4()
        mock_conn.execute.return_value = 'UPDATE 1'  # Soft delete uses UPDATE

        result = await goal_repo.delete_goal(goal_id)

        assert result is True
        mock_conn.execute.assert_called_once()

    async def test_delete_goal_not_found(self, goal_repo, mock_conn):
        """Should return False when goal doesn't exist."""
        goal_id = uuid4()
        mock_conn.execute.return_value = 'UPDATE 0'  # Soft delete uses UPDATE

        result = await goal_repo.delete_goal(goal_id)

        assert result is False

    # --- reorder_goals tests ---

    async def test_reorder_goals_success(self, goal_repo, mock_conn):
        """Should reorder goals by updating display_order."""
        review_id = uuid4()
        goal_ids = [uuid4(), uuid4(), uuid4()]

        await goal_repo.reorder_goals(review_id, goal_ids)

        # Should call execute for each goal
        assert mock_conn.execute.call_count == len(goal_ids)

    async def test_reorder_goals_preserves_order(self, goal_repo, mock_conn):
        """Should set display_order based on list position."""
        review_id = uuid4()
        goal_ids = [uuid4(), uuid4()]

        await goal_repo.reorder_goals(review_id, goal_ids)

        # Verify orders are 0, 1
        calls = mock_conn.execute.call_args_list
        assert len(calls) == 2

    # --- get_weight_total tests ---

    async def test_get_weight_total(self, goal_repo, mock_conn):
        """Should return sum of all goal weights for a review."""
        review_id = uuid4()
        mock_conn.fetchval.return_value = 100

        total = await goal_repo.get_weight_total(review_id)

        assert total == 100
        mock_conn.fetchval.assert_called_once()
        call_args = mock_conn.fetchval.call_args
        assert 'sum' in call_args[0][0].lower()

    async def test_get_weight_total_no_goals(self, goal_repo, mock_conn):
        """Should return 0 when no goals exist."""
        review_id = uuid4()
        mock_conn.fetchval.return_value = None

        total = await goal_repo.get_weight_total(review_id)

        assert total == 0

    # --- get_goal_count tests ---

    async def test_get_goal_count(self, goal_repo, mock_conn):
        """Should return count of goals for a review."""
        review_id = uuid4()
        mock_conn.fetchval.return_value = 5

        count = await goal_repo.get_goal_count(review_id)

        assert count == 5

    async def test_get_goal_count_empty(self, goal_repo, mock_conn):
        """Should return 0 when no goals exist."""
        review_id = uuid4()
        mock_conn.fetchval.return_value = 0

        count = await goal_repo.get_goal_count(review_id)

        assert count == 0
