# TSS PPM v3.0 - Calibration Repository Tests
"""Tests for calibration sessions repository."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.repositories.calibration import CalibrationRepository


@pytest.mark.asyncio
class TestCalibrationRepository:
    """Tests for CalibrationRepository."""

    @pytest.fixture
    def mock_conn(self):
        """Create a mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    def calibration_repo(self, mock_conn):
        """Create a CalibrationRepository instance with mock connection."""
        return CalibrationRepository(mock_conn)

    @pytest.fixture
    def sample_opco_id(self):
        """Sample OpCo ID."""
        return uuid4()

    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID."""
        return uuid4()

    @pytest.fixture
    def sample_session_row(self, sample_opco_id, sample_user_id):
        """Sample calibration session data as returned from database."""
        return {
            'id': uuid4(),
            'opco_id': sample_opco_id,
            'name': 'Q4 2026 Calibration',
            'description': 'End of year calibration session',
            'review_year': 2026,
            'scope': 'BUSINESS_UNIT',
            'business_unit_id': uuid4(),
            'status': 'PREPARATION',
            'facilitator_id': sample_user_id,
            'created_by': sample_user_id,
            'snapshot_taken_at': None,
            'completed_at': None,
            'notes': None,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }

    # --- create_session tests ---

    async def test_create_session_success(self, calibration_repo, mock_conn, sample_session_row):
        """Should create a calibration session with all fields."""
        mock_conn.fetchrow.return_value = sample_session_row

        result = await calibration_repo.create_session(
            opco_id=sample_session_row['opco_id'],
            name='Q4 2026 Calibration',
            review_year=2026,
            scope='BUSINESS_UNIT',
            created_by=sample_session_row['created_by'],
            description='End of year calibration session',
            business_unit_id=sample_session_row['business_unit_id'],
        )

        assert result is not None
        assert result['name'] == 'Q4 2026 Calibration'
        assert result['status'] == 'PREPARATION'
        mock_conn.fetchrow.assert_called_once()
        call_args = mock_conn.fetchrow.call_args[0][0]
        assert 'INSERT INTO calibration_sessions' in call_args

    async def test_create_session_company_wide(self, calibration_repo, mock_conn, sample_session_row):
        """Should create a company-wide calibration session."""
        sample_session_row['scope'] = 'COMPANY_WIDE'
        sample_session_row['business_unit_id'] = None
        mock_conn.fetchrow.return_value = sample_session_row

        result = await calibration_repo.create_session(
            opco_id=sample_session_row['opco_id'],
            name='Company Calibration',
            review_year=2026,
            scope='COMPANY_WIDE',
            created_by=sample_session_row['created_by'],
        )

        assert result['scope'] == 'COMPANY_WIDE'

    # --- get_session_by_id tests ---

    async def test_get_session_by_id_found(self, calibration_repo, mock_conn, sample_session_row):
        """Should return session when found."""
        mock_conn.fetchrow.return_value = sample_session_row
        session_id = sample_session_row['id']

        result = await calibration_repo.get_session_by_id(session_id)

        assert result is not None
        assert result['id'] == session_id
        mock_conn.fetchrow.assert_called_once()

    async def test_get_session_by_id_not_found(self, calibration_repo, mock_conn):
        """Should return None when session not found."""
        mock_conn.fetchrow.return_value = None

        result = await calibration_repo.get_session_by_id(uuid4())

        assert result is None

    async def test_get_session_by_id_with_opco_filter(self, calibration_repo, mock_conn, sample_session_row):
        """Should filter by OpCo when provided."""
        mock_conn.fetchrow.return_value = sample_session_row
        opco_id = sample_session_row['opco_id']

        result = await calibration_repo.get_session_by_id(
            sample_session_row['id'],
            opco_id=opco_id
        )

        assert result is not None
        call_args = mock_conn.fetchrow.call_args[0][0]
        assert 'opco_id' in call_args

    # --- list_sessions tests ---

    async def test_list_sessions_returns_all(self, calibration_repo, mock_conn, sample_session_row):
        """Should return all sessions for an OpCo."""
        mock_conn.fetch.return_value = [sample_session_row]

        result = await calibration_repo.list_sessions(
            opco_id=sample_session_row['opco_id']
        )

        assert len(result) == 1
        mock_conn.fetch.assert_called_once()

    async def test_list_sessions_filter_by_status(self, calibration_repo, mock_conn, sample_session_row):
        """Should filter sessions by status."""
        mock_conn.fetch.return_value = [sample_session_row]

        result = await calibration_repo.list_sessions(
            opco_id=sample_session_row['opco_id'],
            status='PREPARATION'
        )

        assert len(result) == 1
        call_args = mock_conn.fetch.call_args[0][0]
        assert 'status' in call_args

    async def test_list_sessions_filter_by_year(self, calibration_repo, mock_conn, sample_session_row):
        """Should filter sessions by review year."""
        mock_conn.fetch.return_value = [sample_session_row]

        result = await calibration_repo.list_sessions(
            opco_id=sample_session_row['opco_id'],
            review_year=2026
        )

        assert len(result) == 1
        call_args = mock_conn.fetch.call_args[0][0]
        assert 'review_year' in call_args

    async def test_list_sessions_empty(self, calibration_repo, mock_conn, sample_opco_id):
        """Should return empty list when no sessions exist."""
        mock_conn.fetch.return_value = []

        result = await calibration_repo.list_sessions(opco_id=sample_opco_id)

        assert result == []

    # --- update_session tests ---

    async def test_update_session_success(self, calibration_repo, mock_conn, sample_session_row):
        """Should update session fields."""
        updated_row = {**sample_session_row, 'name': 'Updated Name'}
        mock_conn.fetchrow.return_value = updated_row

        result = await calibration_repo.update_session(
            session_id=sample_session_row['id'],
            name='Updated Name'
        )

        assert result['name'] == 'Updated Name'
        mock_conn.fetchrow.assert_called_once()
        call_args = mock_conn.fetchrow.call_args[0][0]
        assert 'UPDATE calibration_sessions' in call_args

    async def test_update_session_description(self, calibration_repo, mock_conn, sample_session_row):
        """Should update session description."""
        updated_row = {**sample_session_row, 'description': 'New description'}
        mock_conn.fetchrow.return_value = updated_row

        result = await calibration_repo.update_session(
            session_id=sample_session_row['id'],
            description='New description'
        )

        assert result['description'] == 'New description'

    async def test_update_session_not_found(self, calibration_repo, mock_conn):
        """Should return None when session not found."""
        mock_conn.fetchrow.return_value = None

        result = await calibration_repo.update_session(
            session_id=uuid4(),
            name='New Name'
        )

        assert result is None

    # --- delete_session tests ---

    async def test_delete_session_draft_success(self, calibration_repo, mock_conn, sample_session_row):
        """Should delete a draft session."""
        mock_conn.fetchrow.return_value = sample_session_row
        mock_conn.execute.return_value = 'DELETE 1'

        result = await calibration_repo.delete_session(sample_session_row['id'])

        assert result is True
        mock_conn.execute.assert_called_once()

    async def test_delete_session_not_found(self, calibration_repo, mock_conn):
        """Should return False when session not found."""
        mock_conn.fetchrow.return_value = None

        result = await calibration_repo.delete_session(uuid4())

        assert result is False

    async def test_delete_session_not_draft(self, calibration_repo, mock_conn, sample_session_row):
        """Should not delete non-draft session."""
        sample_session_row['status'] = 'IN_PROGRESS'
        mock_conn.fetchrow.return_value = sample_session_row

        result = await calibration_repo.delete_session(sample_session_row['id'])

        assert result is False
        mock_conn.execute.assert_not_called()

    # --- status transition tests ---

    async def test_start_session_success(self, calibration_repo, mock_conn, sample_session_row):
        """Should transition session from PREPARATION to IN_PROGRESS."""
        mock_conn.fetchrow.return_value = sample_session_row
        updated_row = {**sample_session_row, 'status': 'IN_PROGRESS'}
        mock_conn.fetchrow.side_effect = [sample_session_row, updated_row]

        result = await calibration_repo.start_session(sample_session_row['id'])

        assert result['status'] == 'IN_PROGRESS'

    async def test_start_session_invalid_status(self, calibration_repo, mock_conn, sample_session_row):
        """Should not start session that's not in PREPARATION."""
        sample_session_row['status'] = 'COMPLETED'
        mock_conn.fetchrow.return_value = sample_session_row

        result = await calibration_repo.start_session(sample_session_row['id'])

        assert result is None

    async def test_complete_session_success(self, calibration_repo, mock_conn, sample_session_row):
        """Should transition session from IN_PROGRESS to COMPLETED."""
        sample_session_row['status'] = 'IN_PROGRESS'
        mock_conn.fetchrow.return_value = sample_session_row
        updated_row = {**sample_session_row, 'status': 'COMPLETED'}
        mock_conn.fetchrow.side_effect = [sample_session_row, updated_row]

        result = await calibration_repo.complete_session(sample_session_row['id'])

        assert result['status'] == 'COMPLETED'

    async def test_complete_session_invalid_status(self, calibration_repo, mock_conn, sample_session_row):
        """Should not complete session that's not IN_PROGRESS."""
        sample_session_row['status'] = 'PREPARATION'
        mock_conn.fetchrow.return_value = sample_session_row

        result = await calibration_repo.complete_session(sample_session_row['id'])

        assert result is None

    # --- add/remove reviews tests ---

    async def test_add_review_to_session(self, calibration_repo, mock_conn):
        """Should add a review to a session."""
        session_id = uuid4()
        review_id = uuid4()
        user_id = uuid4()
        mock_conn.execute.return_value = 'INSERT 0 1'

        result = await calibration_repo.add_review_to_session(
            session_id=session_id,
            review_id=review_id,
            added_by=user_id
        )

        assert result is True
        mock_conn.execute.assert_called_once()
        call_args = mock_conn.execute.call_args[0][0]
        assert 'INSERT INTO calibration_session_reviews' in call_args

    async def test_remove_review_from_session(self, calibration_repo, mock_conn):
        """Should remove a review from a session."""
        session_id = uuid4()
        review_id = uuid4()
        mock_conn.execute.return_value = 'DELETE 1'

        result = await calibration_repo.remove_review_from_session(
            session_id=session_id,
            review_id=review_id
        )

        assert result is True
        mock_conn.execute.assert_called_once()

    async def test_get_session_reviews(self, calibration_repo, mock_conn):
        """Should return reviews in a session with scores."""
        session_id = uuid4()
        mock_review = {
            'review_id': uuid4(),
            'employee_id': uuid4(),
            'employee_name': 'John Doe',
            'what_score': 2.5,
            'how_score': 2.8,
        }
        mock_conn.fetch.return_value = [mock_review]

        result = await calibration_repo.get_session_reviews(session_id)

        assert len(result) == 1
        assert result[0]['employee_name'] == 'John Doe'

    # --- participant management tests ---

    async def test_add_participant_to_session(self, calibration_repo, mock_conn):
        """Should add a participant to a session."""
        session_id = uuid4()
        user_id = uuid4()
        added_by = uuid4()
        mock_conn.fetchrow.return_value = {
            'id': uuid4(),
            'session_id': session_id,
            'user_id': user_id,
            'role': 'PARTICIPANT',
        }

        result = await calibration_repo.add_participant(
            session_id=session_id,
            user_id=user_id,
            role='PARTICIPANT',
            added_by=added_by
        )

        assert result is not None
        assert result['role'] == 'PARTICIPANT'

    async def test_remove_participant_from_session(self, calibration_repo, mock_conn):
        """Should remove a participant from a session."""
        session_id = uuid4()
        user_id = uuid4()
        mock_conn.execute.return_value = 'DELETE 1'

        result = await calibration_repo.remove_participant(
            session_id=session_id,
            user_id=user_id
        )

        assert result is True

    async def test_get_session_participants(self, calibration_repo, mock_conn):
        """Should return participants in a session."""
        session_id = uuid4()
        mock_participant = {
            'user_id': uuid4(),
            'first_name': 'Jane',
            'last_name': 'HR',
            'role': 'FACILITATOR',
        }
        mock_conn.fetch.return_value = [mock_participant]

        result = await calibration_repo.get_session_participants(session_id)

        assert len(result) == 1
        assert result[0]['role'] == 'FACILITATOR'

    # --- notes tests ---

    async def test_add_session_note(self, calibration_repo, mock_conn):
        """Should add a session-level note."""
        session_id = uuid4()
        user_id = uuid4()
        mock_conn.fetchrow.return_value = {
            'id': uuid4(),
            'session_id': session_id,
            'review_id': None,
            'content': 'Discussion notes',
            'created_by': user_id,
        }

        result = await calibration_repo.add_note(
            session_id=session_id,
            content='Discussion notes',
            created_by=user_id
        )

        assert result is not None
        assert result['content'] == 'Discussion notes'
        assert result['review_id'] is None

    async def test_add_review_note(self, calibration_repo, mock_conn):
        """Should add a review-level note."""
        session_id = uuid4()
        review_id = uuid4()
        user_id = uuid4()
        mock_conn.fetchrow.return_value = {
            'id': uuid4(),
            'session_id': session_id,
            'review_id': review_id,
            'content': 'Employee feedback',
            'created_by': user_id,
        }

        result = await calibration_repo.add_note(
            session_id=session_id,
            content='Employee feedback',
            created_by=user_id,
            review_id=review_id
        )

        assert result is not None
        assert result['review_id'] == review_id

    async def test_get_session_notes(self, calibration_repo, mock_conn):
        """Should return notes for a session."""
        session_id = uuid4()
        mock_notes = [
            {'id': uuid4(), 'content': 'Note 1', 'review_id': None},
            {'id': uuid4(), 'content': 'Note 2', 'review_id': uuid4()},
        ]
        mock_conn.fetch.return_value = mock_notes

        result = await calibration_repo.get_session_notes(session_id)

        assert len(result) == 2

    # --- OpCo isolation tests ---

    async def test_opco_isolation_list_sessions(self, calibration_repo, mock_conn):
        """Should only list sessions for the specified OpCo."""
        opco_id = uuid4()
        mock_conn.fetch.return_value = []

        await calibration_repo.list_sessions(opco_id=opco_id)

        call_args = mock_conn.fetch.call_args[0]
        # Verify opco_id is in the query parameters
        assert opco_id in call_args

    async def test_opco_isolation_create_session(self, calibration_repo, mock_conn, sample_session_row):
        """Should create session with the specified OpCo."""
        mock_conn.fetchrow.return_value = sample_session_row
        opco_id = sample_session_row['opco_id']

        await calibration_repo.create_session(
            opco_id=opco_id,
            name='Test Session',
            review_year=2026,
            scope='COMPANY_WIDE',
            created_by=uuid4()
        )

        call_args = mock_conn.fetchrow.call_args[0]
        assert opco_id in call_args
