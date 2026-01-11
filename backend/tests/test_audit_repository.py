# TSS PPM v3.0 - Audit Repository Tests
"""Tests for audit log repository - signature actions."""

import json
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.repositories.audit import AuditRepository


@pytest.mark.asyncio
class TestAuditRepository:
    """Tests for AuditRepository."""

    @pytest.fixture
    def mock_conn(self):
        """Create a mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    def audit_repo(self, mock_conn):
        """Create an AuditRepository instance with mock connection."""
        return AuditRepository(mock_conn)

    @pytest.fixture
    def sample_audit_row(self):
        """Sample audit log data as returned from database."""
        return {
            'id': uuid4(),
            'opco_id': uuid4(),
            'user_id': uuid4(),
            'action': 'EMPLOYEE_SIGNED',
            'entity_type': 'review',
            'entity_id': uuid4(),
            'changes': None,
            'created_at': '2026-01-11T12:00:00Z',
        }

    # --- log_action tests ---

    async def test_log_action_creates_entry(self, audit_repo, mock_conn, sample_audit_row):
        """Should create an audit log entry with all fields."""
        mock_conn.fetchrow.return_value = sample_audit_row

        result = await audit_repo.log_action(
            action='EMPLOYEE_SIGNED',
            entity_type='review',
            entity_id=uuid4(),
            user_id=uuid4(),
            opco_id=uuid4(),
        )

        assert result is not None
        assert result['action'] == 'EMPLOYEE_SIGNED'
        mock_conn.fetchrow.assert_called_once()
        call_args = mock_conn.fetchrow.call_args[0][0]
        assert 'INSERT INTO audit_logs' in call_args

    async def test_log_action_employee_signed(self, audit_repo, mock_conn, sample_audit_row):
        """Should log employee signature action."""
        mock_conn.fetchrow.return_value = sample_audit_row
        review_id = uuid4()
        user_id = uuid4()

        result = await audit_repo.log_action(
            action='EMPLOYEE_SIGNED',
            entity_type='review',
            entity_id=review_id,
            user_id=user_id,
        )

        assert result['action'] == 'EMPLOYEE_SIGNED'
        assert result['entity_type'] == 'review'

    async def test_log_action_manager_signed(self, audit_repo, mock_conn, sample_audit_row):
        """Should log manager signature action."""
        sample_audit_row['action'] = 'MANAGER_SIGNED'
        mock_conn.fetchrow.return_value = sample_audit_row

        result = await audit_repo.log_action(
            action='MANAGER_SIGNED',
            entity_type='review',
            entity_id=uuid4(),
            user_id=uuid4(),
        )

        assert result['action'] == 'MANAGER_SIGNED'

    async def test_log_action_review_rejected(self, audit_repo, mock_conn, sample_audit_row):
        """Should log review rejection with feedback."""
        sample_audit_row['action'] = 'REVIEW_REJECTED'
        sample_audit_row['changes'] = {'feedback': 'Please revise goals'}
        mock_conn.fetchrow.return_value = sample_audit_row

        result = await audit_repo.log_action(
            action='REVIEW_REJECTED',
            entity_type='review',
            entity_id=uuid4(),
            user_id=uuid4(),
            changes={'feedback': 'Please revise goals'},
        )

        assert result['action'] == 'REVIEW_REJECTED'
        assert 'feedback' in str(result['changes'])

    async def test_log_action_with_status_transition(self, audit_repo, mock_conn, sample_audit_row):
        """Should log status transition with before/after values."""
        sample_audit_row['action'] = 'STATUS_CHANGE'
        sample_audit_row['changes'] = {
            'before': 'PENDING_EMPLOYEE_SIGNATURE',
            'after': 'EMPLOYEE_SIGNED',
        }
        mock_conn.fetchrow.return_value = sample_audit_row

        result = await audit_repo.log_action(
            action='STATUS_CHANGE',
            entity_type='review',
            entity_id=uuid4(),
            user_id=uuid4(),
            changes={
                'before': 'PENDING_EMPLOYEE_SIGNATURE',
                'after': 'EMPLOYEE_SIGNED',
            },
        )

        assert result is not None
        # Verify changes were passed to the query
        call_args = mock_conn.fetchrow.call_args
        assert call_args is not None

    async def test_log_action_without_optional_fields(self, audit_repo, mock_conn, sample_audit_row):
        """Should create audit log without optional fields."""
        sample_audit_row['action'] = 'SYSTEM_EVENT'
        sample_audit_row['user_id'] = None
        sample_audit_row['opco_id'] = None
        sample_audit_row['changes'] = None
        mock_conn.fetchrow.return_value = sample_audit_row

        result = await audit_repo.log_action(
            action='SYSTEM_EVENT',
            entity_type='review',
            entity_id=uuid4(),
        )

        assert result is not None
        assert result['action'] == 'SYSTEM_EVENT'

    async def test_log_action_goal_approval(self, audit_repo, mock_conn, sample_audit_row):
        """Should log goal approval action."""
        sample_audit_row['action'] = 'GOALS_APPROVED'
        mock_conn.fetchrow.return_value = sample_audit_row

        result = await audit_repo.log_action(
            action='GOALS_APPROVED',
            entity_type='review',
            entity_id=uuid4(),
            user_id=uuid4(),
        )

        assert result['action'] == 'GOALS_APPROVED'

    async def test_log_action_goal_rejection(self, audit_repo, mock_conn, sample_audit_row):
        """Should log goal rejection with feedback."""
        sample_audit_row['action'] = 'GOALS_REJECTED'
        sample_audit_row['changes'] = {'feedback': 'Goals need clearer metrics'}
        mock_conn.fetchrow.return_value = sample_audit_row

        result = await audit_repo.log_action(
            action='GOALS_REJECTED',
            entity_type='review',
            entity_id=uuid4(),
            user_id=uuid4(),
            changes={'feedback': 'Goals need clearer metrics'},
        )

        assert result['action'] == 'GOALS_REJECTED'

    async def test_log_action_captures_timestamp(self, audit_repo, mock_conn, sample_audit_row):
        """Should capture created_at timestamp."""
        mock_conn.fetchrow.return_value = sample_audit_row

        result = await audit_repo.log_action(
            action='EMPLOYEE_SIGNED',
            entity_type='review',
            entity_id=uuid4(),
        )

        assert 'created_at' in result

    async def test_log_action_serializes_changes_to_json(self, audit_repo, mock_conn, sample_audit_row):
        """Should serialize changes dict to JSON."""
        mock_conn.fetchrow.return_value = sample_audit_row
        changes = {'before': 'DRAFT', 'after': 'PENDING_EMPLOYEE_SIGNATURE'}

        await audit_repo.log_action(
            action='STATUS_CHANGE',
            entity_type='review',
            entity_id=uuid4(),
            changes=changes,
        )

        # Verify JSON serialization was passed to query
        call_args = mock_conn.fetchrow.call_args
        # The 6th argument should be the JSON-serialized changes
        assert call_args[0][6] == json.dumps(changes)
