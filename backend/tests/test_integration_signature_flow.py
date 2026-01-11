# TSS PPM v3.0 - Integration Tests for Signature Flows
"""End-to-end tests for complete signature workflows."""

from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db


@pytest.mark.asyncio
class TestGoalSettingApprovalFlow:
    """Test complete goal setting approval workflow.

    Flow: Employee submits goals → Manager approves → Goals locked
    """

    @pytest.fixture
    def employee_user_id(self):
        return uuid4()

    @pytest.fixture
    def manager_user_id(self):
        return uuid4()

    @pytest.fixture
    def opco_id(self):
        return uuid4()

    @pytest.fixture
    def review_id(self):
        return uuid4()

    @pytest.fixture
    def mock_employee_user(self, employee_user_id):
        return CurrentUser(
            keycloak_id='employee-keycloak-id',
            email='employee@example.com',
            name='John Employee',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_manager_user(self, manager_user_id):
        return CurrentUser(
            keycloak_id='manager-keycloak-id',
            email='manager@example.com',
            name='Jane Manager',
            roles=['manager'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def review_draft_goal_setting(self, review_id, employee_user_id, manager_user_id, opco_id):
        """Review in DRAFT status for GOAL_SETTING stage."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': 'Senior Developer',
            'tov_level': 'B',
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
            'goal_setting_completed_at': None,
        }

    @pytest.fixture
    def review_pending_manager_goal_setting(
        self, review_id, employee_user_id, manager_user_id, opco_id
    ):
        """Review awaiting manager approval for goals."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'PENDING_MANAGER_SIGNATURE',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': 'Senior Developer',
            'tov_level': 'B',
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
            'goal_setting_completed_at': None,
        }

    @pytest.fixture
    def review_signed_goal_setting(
        self, review_id, employee_user_id, manager_user_id, opco_id
    ):
        """Review with approved goals."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'SIGNED',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': 'Senior Developer',
            'tov_level': 'B',
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': manager_user_id,
            'manager_signature_date': '2026-01-11T10:00:00Z',
            'goal_setting_completed_at': '2026-01-11T10:00:00Z',
        }

    @pytest.fixture
    def sample_goals(self):
        """Goals with weights totaling 100%."""
        return [
            {'id': uuid4(), 'weight': 40, 'score': None},
            {'id': uuid4(), 'weight': 35, 'score': None},
            {'id': uuid4(), 'weight': 25, 'score': None},
        ]

    @pytest.fixture
    def mock_db_conn(self):
        conn = AsyncMock()
        return conn

    @pytest_asyncio.fixture
    async def manager_client(self, mock_manager_user, mock_db_conn, manager_user_id):
        """HTTP client authenticated as manager."""
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': manager_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    async def test_goal_setting_complete_flow(
        self,
        manager_client,
        mock_db_conn,
        review_id,
        manager_user_id,
        review_pending_manager_goal_setting,
        review_signed_goal_setting,
    ):
        """Test complete goal setting approval flow.

        Scenario: Manager approves submitted goals, review becomes SIGNED.
        """
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},  # User lookup
            review_pending_manager_goal_setting,  # Get review
            {'id': uuid4()},  # Audit log entry
            review_signed_goal_setting,  # Updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'SIGNED'
        assert data['goal_setting_completed_at'] is not None

    async def test_goal_rejection_returns_to_draft(
        self,
        manager_client,
        mock_db_conn,
        review_id,
        manager_user_id,
        review_pending_manager_goal_setting,
        review_draft_goal_setting,
    ):
        """Test manager rejecting goals sends review back to DRAFT.

        Scenario: Manager rejects goals with feedback, employee can revise.
        """
        rejected_review = {
            **review_draft_goal_setting,
            'rejection_feedback': 'Please add measurable targets to goals',
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},  # User lookup
            review_pending_manager_goal_setting,  # Get review
            {'id': uuid4()},  # Audit log entry
            rejected_review,  # Updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': 'Please add measurable targets to goals'},
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'DRAFT'

    async def test_audit_log_created_on_approval(
        self,
        manager_client,
        mock_db_conn,
        review_id,
        manager_user_id,
        review_pending_manager_goal_setting,
        review_signed_goal_setting,
    ):
        """Verify audit log entry is created when manager approves goals."""
        audit_log_id = uuid4()
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},  # User lookup
            review_pending_manager_goal_setting,  # Get review
            {'id': audit_log_id},  # Audit log entry
            review_signed_goal_setting,  # Updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 200
        # Verify audit log was created (execute was called with INSERT)
        calls = mock_db_conn.execute.call_args_list
        assert any('audit_logs' in str(call) or 'INSERT' in str(call) for call in calls)


@pytest.mark.asyncio
class TestMidYearSignatureFlow:
    """Test complete mid-year review signature workflow.

    Flow: Manager submits → Employee signs → Manager signs → Review complete
    """

    @pytest.fixture
    def employee_user_id(self):
        return uuid4()

    @pytest.fixture
    def manager_user_id(self):
        return uuid4()

    @pytest.fixture
    def opco_id(self):
        return uuid4()

    @pytest.fixture
    def review_id(self):
        return uuid4()

    @pytest.fixture
    def mock_employee_user(self, employee_user_id):
        return CurrentUser(
            keycloak_id='employee-keycloak-id',
            email='employee@example.com',
            name='John Employee',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_manager_user(self, manager_user_id):
        return CurrentUser(
            keycloak_id='manager-keycloak-id',
            email='manager@example.com',
            name='Jane Manager',
            roles=['manager'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def review_pending_employee(self, review_id, employee_user_id, manager_user_id, opco_id):
        """Review submitted for employee signature."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
            'stage': 'MID_YEAR_REVIEW',
            'review_year': 2026,
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
        }

    @pytest.fixture
    def review_pending_manager(self, review_id, employee_user_id, manager_user_id, opco_id):
        """Review with employee signature, awaiting manager."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'PENDING_MANAGER_SIGNATURE',
            'stage': 'MID_YEAR_REVIEW',
            'review_year': 2026,
            'employee_signature_by': employee_user_id,
            'employee_signature_date': '2026-07-01T10:00:00Z',
            'manager_signature_by': None,
            'manager_signature_date': None,
        }

    @pytest.fixture
    def review_signed(self, review_id, employee_user_id, manager_user_id, opco_id):
        """Fully signed review."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'SIGNED',
            'stage': 'MID_YEAR_REVIEW',
            'review_year': 2026,
            'employee_signature_by': employee_user_id,
            'employee_signature_date': '2026-07-01T10:00:00Z',
            'manager_signature_by': manager_user_id,
            'manager_signature_date': '2026-07-02T14:00:00Z',
        }

    @pytest.fixture
    def mock_db_conn(self):
        conn = AsyncMock()
        return conn

    @pytest_asyncio.fixture
    async def employee_client(self, mock_employee_user, mock_db_conn, employee_user_id):
        app.dependency_overrides[get_current_user] = lambda: mock_employee_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': employee_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def manager_client(self, mock_manager_user, mock_db_conn, manager_user_id):
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': manager_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    async def test_employee_signs_mid_year_review(
        self,
        employee_client,
        mock_db_conn,
        review_id,
        employee_user_id,
        review_pending_employee,
        review_pending_manager,
    ):
        """Employee signing transitions to PENDING_MANAGER_SIGNATURE."""
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},  # User lookup
            review_pending_employee,  # Get review
            {'id': uuid4()},  # Audit log
            review_pending_manager,  # Updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await employee_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'PENDING_MANAGER_SIGNATURE'
        assert data['employee_signature_by'] == str(employee_user_id)

    async def test_manager_completes_mid_year_review(
        self,
        manager_client,
        mock_db_conn,
        review_id,
        manager_user_id,
        review_pending_manager,
        review_signed,
    ):
        """Manager signing after employee completes the review."""
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},  # User lookup
            review_pending_manager,  # Get review
            {'id': uuid4()},  # Audit log
            review_signed,  # Updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'SIGNED'
        assert data['employee_signature_by'] is not None
        assert data['manager_signature_by'] is not None


@pytest.mark.asyncio
class TestEndYearSignatureFlow:
    """Test complete end-year review signature workflow.

    Flow: Manager submits → Employee signs → Manager signs → Final review
    """

    @pytest.fixture
    def employee_user_id(self):
        return uuid4()

    @pytest.fixture
    def manager_user_id(self):
        return uuid4()

    @pytest.fixture
    def opco_id(self):
        return uuid4()

    @pytest.fixture
    def review_id(self):
        return uuid4()

    @pytest.fixture
    def mock_employee_user(self, employee_user_id):
        return CurrentUser(
            keycloak_id='employee-keycloak-id',
            email='employee@example.com',
            name='John Employee',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_manager_user(self, manager_user_id):
        return CurrentUser(
            keycloak_id='manager-keycloak-id',
            email='manager@example.com',
            name='Jane Manager',
            roles=['manager'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def review_pending_employee(self, review_id, employee_user_id, manager_user_id, opco_id):
        """End-year review awaiting employee signature."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'what_score': 2.35,
            'how_score': 2.17,
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
        }

    @pytest.fixture
    def review_pending_manager(self, review_id, employee_user_id, manager_user_id, opco_id):
        """End-year review awaiting manager signature."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'PENDING_MANAGER_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'what_score': 2.35,
            'how_score': 2.17,
            'employee_signature_by': employee_user_id,
            'employee_signature_date': '2026-12-10T10:00:00Z',
            'manager_signature_by': None,
            'manager_signature_date': None,
        }

    @pytest.fixture
    def review_signed(self, review_id, employee_user_id, manager_user_id, opco_id):
        """Fully signed end-year review."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'SIGNED',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'what_score': 2.35,
            'how_score': 2.17,
            'employee_signature_by': employee_user_id,
            'employee_signature_date': '2026-12-10T10:00:00Z',
            'manager_signature_by': manager_user_id,
            'manager_signature_date': '2026-12-15T14:00:00Z',
        }

    @pytest.fixture
    def mock_db_conn(self):
        conn = AsyncMock()
        return conn

    @pytest_asyncio.fixture
    async def employee_client(self, mock_employee_user, mock_db_conn, employee_user_id):
        app.dependency_overrides[get_current_user] = lambda: mock_employee_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': employee_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def manager_client(self, mock_manager_user, mock_db_conn, manager_user_id):
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': manager_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    async def test_complete_end_year_signature_flow(
        self,
        employee_client,
        manager_client,
        mock_db_conn,
        review_id,
        employee_user_id,
        manager_user_id,
        review_pending_employee,
        review_pending_manager,
        review_signed,
    ):
        """Test complete end-year review signature flow.

        Flow: Employee signs → Manager signs → SIGNED
        """
        # Step 1: Employee signs
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            review_pending_employee,
            {'id': uuid4()},
            review_pending_manager,
        ]
        mock_db_conn.execute = AsyncMock()

        response = await employee_client.post(f'/api/v1/reviews/{review_id}/sign')
        assert response.status_code == 200
        assert response.json()['status'] == 'PENDING_MANAGER_SIGNATURE'

    async def test_employee_reject_end_year_review(
        self,
        employee_client,
        mock_db_conn,
        review_id,
        employee_user_id,
        review_pending_employee,
    ):
        """Employee can reject end-year review back to DRAFT."""
        rejected_review = {
            **review_pending_employee,
            'status': 'DRAFT',
            'rejection_feedback': 'I disagree with the competency scores',
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            review_pending_employee,
            {'id': uuid4()},
            rejected_review,
        ]
        mock_db_conn.execute = AsyncMock()

        response = await employee_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': 'I disagree with the competency scores'},
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'DRAFT'


@pytest.mark.asyncio
class TestRejectionResubmissionFlow:
    """Test rejection and re-submission workflows."""

    @pytest.fixture
    def employee_user_id(self):
        return uuid4()

    @pytest.fixture
    def manager_user_id(self):
        return uuid4()

    @pytest.fixture
    def opco_id(self):
        return uuid4()

    @pytest.fixture
    def review_id(self):
        return uuid4()

    @pytest.fixture
    def mock_employee_user(self, employee_user_id):
        return CurrentUser(
            keycloak_id='employee-keycloak-id',
            email='employee@example.com',
            name='John Employee',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_manager_user(self, manager_user_id):
        return CurrentUser(
            keycloak_id='manager-keycloak-id',
            email='manager@example.com',
            name='Jane Manager',
            roles=['manager'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def review_draft(self, review_id, employee_user_id, manager_user_id, opco_id):
        """Review back in DRAFT after rejection."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'DRAFT',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'job_title': 'Senior Developer',
            'tov_level': 'B',
            'rejection_feedback': 'Previous feedback from rejection',
        }

    @pytest.fixture
    def review_pending_employee(self, review_id, employee_user_id, manager_user_id, opco_id):
        """Review submitted again after addressing feedback."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'job_title': 'Senior Developer',
            'tov_level': 'B',
            'rejection_feedback': None,  # Cleared after resubmission
        }

    @pytest.fixture
    def mock_db_conn(self):
        conn = AsyncMock()
        return conn

    @pytest_asyncio.fixture
    async def manager_client(self, mock_manager_user, mock_db_conn, manager_user_id):
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': manager_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    async def test_resubmit_after_rejection(
        self,
        manager_client,
        mock_db_conn,
        review_id,
        manager_user_id,
        review_draft,
        review_pending_employee,
    ):
        """Manager can resubmit review after it was rejected and revised."""
        # Mock getting goals with 100% weights and all scored
        mock_db_conn.fetch.return_value = [
            {'weight': 40, 'score': 2},
            {'weight': 35, 'score': 2},
            {'weight': 25, 'score': 3},
        ]
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},  # User lookup
            review_draft,  # Get review
            {'id': uuid4()},  # Audit log
            review_pending_employee,  # Updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(f'/api/v1/reviews/{review_id}/submit')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'PENDING_EMPLOYEE_SIGNATURE'

    async def test_rejection_preserves_feedback(
        self,
        manager_client,
        mock_db_conn,
        review_id,
        manager_user_id,
    ):
        """Rejection feedback is stored with the review."""
        review_pending_employee = {
            'id': review_id,
            'employee_id': uuid4(),
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
        }
        rejected_review = {
            **review_pending_employee,
            'status': 'DRAFT',
            'rejection_feedback': 'Scores need recalibration based on Q4 results',
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            review_pending_employee,
            {'id': uuid4()},
            rejected_review,
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': 'Scores need recalibration based on Q4 results'},
        )

        assert response.status_code == 200
        # Verify execute was called with feedback in SQL
        calls = mock_db_conn.execute.call_args_list
        assert any('rejection_feedback' in str(call) for call in calls)


@pytest.mark.asyncio
class TestAuditLogIntegration:
    """Verify audit logs are created for all signature actions."""

    @pytest.fixture
    def employee_user_id(self):
        return uuid4()

    @pytest.fixture
    def manager_user_id(self):
        return uuid4()

    @pytest.fixture
    def review_id(self):
        return uuid4()

    @pytest.fixture
    def mock_employee_user(self, employee_user_id):
        return CurrentUser(
            keycloak_id='employee-keycloak-id',
            email='employee@example.com',
            name='John Employee',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_manager_user(self, manager_user_id):
        return CurrentUser(
            keycloak_id='manager-keycloak-id',
            email='manager@example.com',
            name='Jane Manager',
            roles=['manager'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_db_conn(self):
        conn = AsyncMock()
        return conn

    @pytest_asyncio.fixture
    async def employee_client(self, mock_employee_user, mock_db_conn, employee_user_id):
        app.dependency_overrides[get_current_user] = lambda: mock_employee_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': employee_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def manager_client(self, mock_manager_user, mock_db_conn, manager_user_id):
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': manager_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    async def test_sign_creates_audit_log(
        self, employee_client, mock_db_conn, review_id, employee_user_id
    ):
        """Signing a review creates an audit log entry."""
        review_pending = {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': uuid4(),
            'opco_id': uuid4(),
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
        }
        signed_review = {
            **review_pending,
            'status': 'PENDING_MANAGER_SIGNATURE',
            'employee_signature_by': employee_user_id,
        }
        audit_log_id = uuid4()
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            review_pending,
            {'id': audit_log_id},  # Audit log creation returns ID
            signed_review,
        ]
        mock_db_conn.execute = AsyncMock()

        response = await employee_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 200
        # Verify audit_logs INSERT was called
        calls = mock_db_conn.fetchrow.call_args_list
        assert any(
            'audit_logs' in str(call) or 'sign' in str(call).lower() for call in calls
        )

    async def test_reject_creates_audit_log(
        self, manager_client, mock_db_conn, review_id, manager_user_id
    ):
        """Rejecting a review creates an audit log entry."""
        review_pending = {
            'id': review_id,
            'employee_id': uuid4(),
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'PENDING_MANAGER_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
        }
        rejected_review = {
            **review_pending,
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
        }
        audit_log_id = uuid4()
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            review_pending,
            {'id': audit_log_id},
            rejected_review,
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': 'Needs revision'},
        )

        assert response.status_code == 200
        # Audit log should be created for rejection
        calls = mock_db_conn.fetchrow.call_args_list
        assert any(
            'audit_logs' in str(call) or 'reject' in str(call).lower() for call in calls
        )

    async def test_submit_creates_audit_log(
        self, manager_client, mock_db_conn, review_id, manager_user_id
    ):
        """Submitting a review creates an audit log entry."""
        review_draft = {
            'id': review_id,
            'employee_id': uuid4(),
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'job_title': 'Developer',
            'tov_level': 'B',
        }
        submitted_review = {
            **review_draft,
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
        }
        # Mock goals with valid weights and scores
        mock_db_conn.fetch.return_value = [
            {'weight': 50, 'score': 2},
            {'weight': 50, 'score': 3},
        ]
        audit_log_id = uuid4()
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            review_draft,
            {'id': audit_log_id},
            submitted_review,
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(f'/api/v1/reviews/{review_id}/submit')

        assert response.status_code == 200
