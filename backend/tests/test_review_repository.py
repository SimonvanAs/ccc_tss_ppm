# TSS PPM v3.0 - Review Repository Tests
"""Tests for ReviewRepository with new header fields."""

from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, timezone

import pytest


class TestReviewRepositoryGetReview:
    """Tests for ReviewRepository.get_review with header fields."""

    @pytest.fixture
    def mock_conn(self):
        """Create a mock database connection."""
        return AsyncMock()

    @pytest.fixture
    def sample_review_with_header(self):
        """Sample review data including header fields."""
        return {
            'id': uuid4(),
            'employee_id': uuid4(),
            'manager_id': uuid4(),
            'opco_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'what_score': None,
            'how_score': None,
            'job_title': 'Senior Developer',
            'tov_level': 'B',
            'goal_setting_completed_at': None,
            'mid_year_completed_at': None,
            'end_year_completed_at': None,
            'employee_name': 'John Doe',
            'manager_name': 'Jane Smith',
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }

    async def test_get_review_returns_job_title(self, mock_conn, sample_review_with_header):
        """get_review should return job_title field."""
        from src.routers.reviews import ReviewRepository

        mock_conn.fetchrow.return_value = sample_review_with_header
        repo = ReviewRepository(mock_conn)

        result = await repo.get_review(sample_review_with_header['id'])

        assert result is not None
        assert 'job_title' in result
        assert result['job_title'] == 'Senior Developer'

    async def test_get_review_returns_tov_level(self, mock_conn, sample_review_with_header):
        """get_review should return tov_level field."""
        from src.routers.reviews import ReviewRepository

        mock_conn.fetchrow.return_value = sample_review_with_header
        repo = ReviewRepository(mock_conn)

        result = await repo.get_review(sample_review_with_header['id'])

        assert result is not None
        assert 'tov_level' in result
        assert result['tov_level'] == 'B'

    async def test_get_review_returns_stage_completion_timestamps(
        self, mock_conn, sample_review_with_header
    ):
        """get_review should return stage completion timestamps."""
        from src.routers.reviews import ReviewRepository

        completed_at = datetime.now(timezone.utc)
        sample_review_with_header['goal_setting_completed_at'] = completed_at
        mock_conn.fetchrow.return_value = sample_review_with_header
        repo = ReviewRepository(mock_conn)

        result = await repo.get_review(sample_review_with_header['id'])

        assert result is not None
        assert 'goal_setting_completed_at' in result
        assert 'mid_year_completed_at' in result
        assert 'end_year_completed_at' in result
        assert result['goal_setting_completed_at'] == completed_at

    async def test_get_review_returns_employee_name(self, mock_conn, sample_review_with_header):
        """get_review should return employee name from joined user table."""
        from src.routers.reviews import ReviewRepository

        mock_conn.fetchrow.return_value = sample_review_with_header
        repo = ReviewRepository(mock_conn)

        result = await repo.get_review(sample_review_with_header['id'])

        assert result is not None
        assert 'employee_name' in result
        assert result['employee_name'] == 'John Doe'

    async def test_get_review_returns_manager_name(self, mock_conn, sample_review_with_header):
        """get_review should return manager name from joined user table."""
        from src.routers.reviews import ReviewRepository

        mock_conn.fetchrow.return_value = sample_review_with_header
        repo = ReviewRepository(mock_conn)

        result = await repo.get_review(sample_review_with_header['id'])

        assert result is not None
        assert 'manager_name' in result
        assert result['manager_name'] == 'Jane Smith'

    async def test_get_review_query_joins_users_table(self, mock_conn, sample_review_with_header):
        """get_review SQL should join with users table for names."""
        from src.routers.reviews import ReviewRepository

        mock_conn.fetchrow.return_value = sample_review_with_header
        repo = ReviewRepository(mock_conn)

        await repo.get_review(sample_review_with_header['id'])

        # Verify the query joins with users table
        call_args = mock_conn.fetchrow.call_args
        sql_query = call_args[0][0].lower()
        assert 'join' in sql_query or 'users' in sql_query


class TestReviewRepositoryUpdateReview:
    """Tests for ReviewRepository.update_review with job_title and tov_level."""

    @pytest.fixture
    def mock_conn(self):
        """Create a mock database connection."""
        return AsyncMock()

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
            'job_title': 'Senior Developer',
            'tov_level': 'B',
        }

    async def test_update_review_job_title(self, mock_conn, sample_review):
        """update_review should update job_title field."""
        from src.routers.reviews import ReviewRepository

        updated_review = {**sample_review, 'job_title': 'Lead Developer'}
        mock_conn.fetchrow.return_value = updated_review
        repo = ReviewRepository(mock_conn)

        result = await repo.update_review(
            sample_review['id'],
            job_title='Lead Developer',
        )

        assert result is not None
        assert result['job_title'] == 'Lead Developer'
        # Verify SQL contains job_title
        call_args = mock_conn.fetchrow.call_args
        sql_query = call_args[0][0].lower()
        assert 'job_title' in sql_query

    async def test_update_review_tov_level(self, mock_conn, sample_review):
        """update_review should update tov_level field."""
        from src.routers.reviews import ReviewRepository

        updated_review = {**sample_review, 'tov_level': 'C'}
        mock_conn.fetchrow.return_value = updated_review
        repo = ReviewRepository(mock_conn)

        result = await repo.update_review(
            sample_review['id'],
            tov_level='C',
        )

        assert result is not None
        assert result['tov_level'] == 'C'
        # Verify SQL contains tov_level
        call_args = mock_conn.fetchrow.call_args
        sql_query = call_args[0][0].lower()
        assert 'tov_level' in sql_query

    async def test_update_review_both_fields(self, mock_conn, sample_review):
        """update_review should update both job_title and tov_level."""
        from src.routers.reviews import ReviewRepository

        updated_review = {
            **sample_review,
            'job_title': 'Lead Developer',
            'tov_level': 'C',
        }
        mock_conn.fetchrow.return_value = updated_review
        repo = ReviewRepository(mock_conn)

        result = await repo.update_review(
            sample_review['id'],
            job_title='Lead Developer',
            tov_level='C',
        )

        assert result is not None
        assert result['job_title'] == 'Lead Developer'
        assert result['tov_level'] == 'C'

    async def test_update_review_returns_none_for_not_found(self, mock_conn):
        """update_review should return None if review not found."""
        from src.routers.reviews import ReviewRepository

        mock_conn.fetchrow.return_value = None
        repo = ReviewRepository(mock_conn)

        result = await repo.update_review(
            uuid4(),
            job_title='Lead Developer',
        )

        assert result is None


class TestReviewRepositoryManagerReassignment:
    """Tests for ReviewRepository.reassign_manager."""

    @pytest.fixture
    def mock_conn(self):
        """Create a mock database connection."""
        return AsyncMock()

    @pytest.fixture
    def sample_review(self):
        """Sample review data."""
        old_manager_id = uuid4()
        new_manager_id = uuid4()
        return {
            'id': uuid4(),
            'employee_id': uuid4(),
            'manager_id': old_manager_id,
            'opco_id': uuid4(),
            'status': 'DRAFT',
            'old_manager_id': old_manager_id,
            'new_manager_id': new_manager_id,
        }

    async def test_reassign_manager_updates_manager_id(self, mock_conn, sample_review):
        """reassign_manager should update manager_id field."""
        from src.routers.reviews import ReviewRepository

        new_manager_id = sample_review['new_manager_id']
        updated_review = {**sample_review, 'manager_id': new_manager_id}
        mock_conn.fetchrow.return_value = updated_review
        repo = ReviewRepository(mock_conn)

        result = await repo.reassign_manager(
            sample_review['id'],
            new_manager_id,
        )

        assert result is not None
        assert result['manager_id'] == new_manager_id

    async def test_reassign_manager_query_updates_manager(self, mock_conn, sample_review):
        """reassign_manager SQL should update manager_id."""
        from src.routers.reviews import ReviewRepository

        new_manager_id = sample_review['new_manager_id']
        updated_review = {**sample_review, 'manager_id': new_manager_id}
        mock_conn.fetchrow.return_value = updated_review
        repo = ReviewRepository(mock_conn)

        await repo.reassign_manager(sample_review['id'], new_manager_id)

        # Verify SQL updates manager_id
        call_args = mock_conn.fetchrow.call_args
        sql_query = call_args[0][0].lower()
        assert 'manager_id' in sql_query
        assert 'update' in sql_query

    async def test_reassign_manager_returns_none_for_not_found(self, mock_conn):
        """reassign_manager should return None if review not found."""
        from src.routers.reviews import ReviewRepository

        mock_conn.fetchrow.return_value = None
        repo = ReviewRepository(mock_conn)

        result = await repo.reassign_manager(uuid4(), uuid4())

        assert result is None
