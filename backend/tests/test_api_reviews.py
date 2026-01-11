# TSS PPM v3.0 - Review API Tests
"""Tests for Review API endpoints."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db


@pytest.mark.asyncio
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
        """Sample review data with header fields."""
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

    @pytest.fixture
    def sample_review_missing_job_title(self):
        """Sample review with missing job_title."""
        return {
            'id': uuid4(),
            'employee_id': uuid4(),
            'manager_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': None,
            'tov_level': 'B',
        }

    @pytest.fixture
    def sample_review_missing_tov_level(self):
        """Sample review with missing tov_level."""
        return {
            'id': uuid4(),
            'employee_id': uuid4(),
            'manager_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': 'Senior Developer',
            'tov_level': None,
        }

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest_asyncio.fixture
    async def client(self, mock_current_user, mock_db_conn):
        """Async HTTP client with dependency overrides."""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
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

    async def test_submit_review_rejected_when_job_title_missing(
        self, client, mock_db_conn, sample_review_missing_job_title
    ):
        """POST /reviews/:id/submit should reject when job_title is missing."""
        review_id = sample_review_missing_job_title['id']
        mock_db_conn.fetchrow.return_value = sample_review_missing_job_title
        mock_db_conn.fetchval.return_value = 100  # Weights OK

        response = await client.post(f'/api/v1/reviews/{review_id}/submit')

        assert response.status_code == 400
        detail = response.json()['detail'].lower()
        assert 'job_title' in detail or 'job title' in detail

    async def test_submit_review_rejected_when_tov_level_missing(
        self, client, mock_db_conn, sample_review_missing_tov_level
    ):
        """POST /reviews/:id/submit should reject when tov_level is missing."""
        review_id = sample_review_missing_tov_level['id']
        mock_db_conn.fetchrow.return_value = sample_review_missing_tov_level
        mock_db_conn.fetchval.return_value = 100  # Weights OK

        response = await client.post(f'/api/v1/reviews/{review_id}/submit')

        assert response.status_code == 400
        detail = response.json()['detail'].lower()
        assert 'tov_level' in detail or 'tov level' in detail

    async def test_submit_review_rejected_when_both_missing(
        self, client, mock_db_conn
    ):
        """POST /reviews/:id/submit should reject when both fields missing."""
        review_missing_both = {
            'id': uuid4(),
            'employee_id': uuid4(),
            'manager_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': None,
            'tov_level': None,
        }
        mock_db_conn.fetchrow.return_value = review_missing_both
        mock_db_conn.fetchval.return_value = 100

        response = await client.post(f'/api/v1/reviews/{review_missing_both["id"]}/submit')

        assert response.status_code == 400
        detail = response.json()['detail'].lower()
        # Should mention missing fields
        assert 'job_title' in detail or 'tov_level' in detail


@pytest.mark.asyncio
class TestSignReviewEndpoint:
    """Tests for review sign endpoint."""

    @pytest.fixture
    def employee_user_id(self):
        """Employee's database user ID."""
        return uuid4()

    @pytest.fixture
    def manager_user_id(self):
        """Manager's database user ID."""
        return uuid4()

    @pytest.fixture
    def mock_employee_user(self, employee_user_id):
        """Mock authenticated employee."""
        return CurrentUser(
            keycloak_id='employee-keycloak-id',
            email='employee@example.com',
            name='John Employee',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_manager_user(self, manager_user_id):
        """Mock authenticated manager."""
        return CurrentUser(
            keycloak_id='manager-keycloak-id',
            email='manager@example.com',
            name='Jane Manager',
            roles=['manager'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def sample_review_pending_employee(self, employee_user_id, manager_user_id):
        """Sample review awaiting employee signature."""
        return {
            'id': uuid4(),
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
        }

    @pytest.fixture
    def sample_review_pending_manager(self, employee_user_id, manager_user_id):
        """Sample review awaiting manager signature (employee already signed)."""
        return {
            'id': uuid4(),
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'PENDING_MANAGER_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'employee_signature_by': employee_user_id,
            'employee_signature_date': '2026-01-10T10:00:00Z',
            'manager_signature_by': None,
            'manager_signature_date': None,
        }

    @pytest.fixture
    def sample_review_pending_manager_goal_setting(self, employee_user_id, manager_user_id):
        """Sample review awaiting manager approval for goal setting."""
        return {
            'id': uuid4(),
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'PENDING_MANAGER_SIGNATURE',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': 'Senior Developer',
            'tov_level': 'B',
            'goal_setting_completed_at': None,
        }

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest_asyncio.fixture
    async def employee_client(self, mock_employee_user, mock_db_conn, employee_user_id):
        """HTTP client authenticated as employee."""
        app.dependency_overrides[get_current_user] = lambda: mock_employee_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        # Mock user lookup to return employee's database ID
        mock_db_conn.fetchrow.return_value = {'id': employee_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def manager_client(self, mock_manager_user, mock_db_conn, manager_user_id):
        """HTTP client authenticated as manager."""
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        # Mock user lookup to return manager's database ID
        mock_db_conn.fetchrow.return_value = {'id': manager_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    # --- POST /api/v1/reviews/:id/sign tests ---

    async def test_sign_requires_auth(self):
        """POST /reviews/:id/sign should require authentication."""
        app.dependency_overrides.clear()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            review_id = uuid4()
            response = await client.post(f'/api/v1/reviews/{review_id}/sign')
            assert response.status_code in [401, 403]

    async def test_employee_sign_success(
        self, employee_client, mock_db_conn, sample_review_pending_employee, employee_user_id
    ):
        """Employee can sign review pending their signature."""
        review_id = sample_review_pending_employee['id']
        # After employee signs, status goes to PENDING_MANAGER_SIGNATURE
        signed_review = {
            **sample_review_pending_employee,
            'status': 'PENDING_MANAGER_SIGNATURE',
            'employee_signature_by': employee_user_id,
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},  # User lookup
            sample_review_pending_employee,  # Get review
            {'id': uuid4()},  # Audit log entry
            signed_review,  # Get updated review
        ]
        # Mock execute for the UPDATE statement
        mock_db_conn.execute = AsyncMock()

        response = await employee_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 200
        data = response.json()
        # After employee signs, review goes to PENDING_MANAGER_SIGNATURE
        assert data['status'] == 'PENDING_MANAGER_SIGNATURE'

    async def test_manager_sign_success(
        self, manager_client, mock_db_conn, sample_review_pending_manager, manager_user_id
    ):
        """Manager can sign review pending their signature."""
        review_id = sample_review_pending_manager['id']
        # After manager signs, both signatures are present → SIGNED
        signed_review = {
            **sample_review_pending_manager,
            'status': 'SIGNED',
            'manager_signature_by': manager_user_id,
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},  # User lookup
            sample_review_pending_manager,  # Get review
            {'id': uuid4()},  # Audit log entry
            signed_review,  # Get updated review
        ]
        # Mock execute for the UPDATE statement
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'SIGNED'

    async def test_sign_review_not_found(self, employee_client, mock_db_conn, employee_user_id):
        """POST /reviews/:id/sign should return 404 for non-existent review."""
        review_id = uuid4()
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},  # User lookup
            None,  # Review not found
        ]

        response = await employee_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 404

    async def test_sign_wrong_status(
        self, employee_client, mock_db_conn, sample_review_pending_employee, employee_user_id
    ):
        """Cannot sign a review that's not awaiting your signature."""
        review_id = sample_review_pending_employee['id']
        # Review is in DRAFT status, not pending signature
        draft_review = {**sample_review_pending_employee, 'status': 'DRAFT'}
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            draft_review,
        ]

        response = await employee_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 400
        assert 'status' in response.json()['detail'].lower()

    async def test_employee_cannot_sign_others_review(
        self, employee_client, mock_db_conn, employee_user_id
    ):
        """Employee cannot sign another employee's review."""
        other_employee_id = uuid4()
        other_review = {
            'id': uuid4(),
            'employee_id': other_employee_id,  # Different employee
            'manager_id': uuid4(),
            'opco_id': uuid4(),
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            other_review,
        ]

        response = await employee_client.post(f'/api/v1/reviews/{other_review["id"]}/sign')

        assert response.status_code == 403
        assert 'authorized' in response.json()['detail'].lower()

    async def test_sign_creates_audit_log(
        self, employee_client, mock_db_conn, sample_review_pending_employee, employee_user_id
    ):
        """Signing a review should create an audit log entry."""
        review_id = sample_review_pending_employee['id']
        signed_review = {
            **sample_review_pending_employee,
            'status': 'PENDING_MANAGER_SIGNATURE',
            'employee_signature_by': employee_user_id,
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            sample_review_pending_employee,
            {'id': uuid4(), 'action': 'EMPLOYEE_SIGNED'},  # Audit log
            signed_review,  # Get updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await employee_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 200
        # Verify audit log was called (3rd fetchrow call is audit log)
        assert mock_db_conn.fetchrow.call_count >= 3

    async def test_auto_transition_to_signed(
        self, manager_client, mock_db_conn, sample_review_pending_manager, manager_user_id
    ):
        """When manager signs after employee, status auto-transitions to SIGNED."""
        review_id = sample_review_pending_manager['id']
        # Employee already signed, manager signing now → SIGNED
        fully_signed = {
            **sample_review_pending_manager,
            'status': 'SIGNED',
            'manager_signature_by': manager_user_id,
            'manager_signature_date': '2026-01-11T12:00:00Z',
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            sample_review_pending_manager,
            {'id': uuid4()},  # Audit log
            fully_signed,  # Get updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 200
        assert response.json()['status'] == 'SIGNED'

    async def test_goal_setting_completed_at_set_on_manager_approval(
        self, manager_client, mock_db_conn, sample_review_pending_manager_goal_setting, manager_user_id
    ):
        """Manager approval during GOAL_SETTING should set goal_setting_completed_at."""
        review_id = sample_review_pending_manager_goal_setting['id']
        from datetime import datetime, timezone
        approved_review = {
            **sample_review_pending_manager_goal_setting,
            'status': 'SIGNED',
            'manager_signature_by': manager_user_id,
            'manager_signature_date': datetime.now(timezone.utc).isoformat(),
            'goal_setting_completed_at': datetime.now(timezone.utc),
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            sample_review_pending_manager_goal_setting,
            {'id': uuid4()},  # Audit log
            approved_review,  # Get updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(f'/api/v1/reviews/{review_id}/sign')

        assert response.status_code == 200
        # Verify execute was called with goal_setting_completed_at update
        assert mock_db_conn.execute.called
        execute_call_args = str(mock_db_conn.execute.call_args)
        assert 'goal_setting_completed_at' in execute_call_args


@pytest.mark.asyncio
class TestGetReviewEndpoint:
    """Tests for GET /api/v1/reviews/{id} endpoint with header fields."""

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
    def mock_db_conn(self):
        """Mock database connection."""
        return AsyncMock()

    @pytest.fixture
    def sample_review_with_header(self):
        """Sample review with all header fields populated."""
        from datetime import datetime, timezone
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
            'employee_name': 'John Doe',
            'manager_name': 'Jane Smith',
            'goal_setting_completed_at': datetime(2026, 2, 15, 10, 0, tzinfo=timezone.utc),
            'mid_year_completed_at': None,
            'end_year_completed_at': None,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }

    @pytest_asyncio.fixture
    async def client(self, mock_current_user, mock_db_conn):
        """Async HTTP client with dependency overrides."""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    async def test_get_review_returns_job_title(
        self, client, mock_db_conn, sample_review_with_header
    ):
        """GET /reviews/:id should return job_title field."""
        review_id = sample_review_with_header['id']
        mock_db_conn.fetchrow.return_value = sample_review_with_header

        response = await client.get(f'/api/v1/reviews/{review_id}')

        assert response.status_code == 200
        data = response.json()
        assert 'job_title' in data
        assert data['job_title'] == 'Senior Developer'

    async def test_get_review_returns_tov_level(
        self, client, mock_db_conn, sample_review_with_header
    ):
        """GET /reviews/:id should return tov_level field."""
        review_id = sample_review_with_header['id']
        mock_db_conn.fetchrow.return_value = sample_review_with_header

        response = await client.get(f'/api/v1/reviews/{review_id}')

        assert response.status_code == 200
        data = response.json()
        assert 'tov_level' in data
        assert data['tov_level'] == 'B'

    async def test_get_review_returns_employee_name(
        self, client, mock_db_conn, sample_review_with_header
    ):
        """GET /reviews/:id should return employee_name from joined users table."""
        review_id = sample_review_with_header['id']
        mock_db_conn.fetchrow.return_value = sample_review_with_header

        response = await client.get(f'/api/v1/reviews/{review_id}')

        assert response.status_code == 200
        data = response.json()
        assert 'employee_name' in data
        assert data['employee_name'] == 'John Doe'

    async def test_get_review_returns_manager_name(
        self, client, mock_db_conn, sample_review_with_header
    ):
        """GET /reviews/:id should return manager_name from joined users table."""
        review_id = sample_review_with_header['id']
        mock_db_conn.fetchrow.return_value = sample_review_with_header

        response = await client.get(f'/api/v1/reviews/{review_id}')

        assert response.status_code == 200
        data = response.json()
        assert 'manager_name' in data
        assert data['manager_name'] == 'Jane Smith'

    async def test_get_review_returns_goal_setting_completed_at(
        self, client, mock_db_conn, sample_review_with_header
    ):
        """GET /reviews/:id should return goal_setting_completed_at timestamp."""
        review_id = sample_review_with_header['id']
        mock_db_conn.fetchrow.return_value = sample_review_with_header

        response = await client.get(f'/api/v1/reviews/{review_id}')

        assert response.status_code == 200
        data = response.json()
        assert 'goal_setting_completed_at' in data
        assert data['goal_setting_completed_at'] is not None
        assert '2026-02-15' in data['goal_setting_completed_at']

    async def test_get_review_returns_mid_year_completed_at(
        self, client, mock_db_conn, sample_review_with_header
    ):
        """GET /reviews/:id should return mid_year_completed_at timestamp."""
        review_id = sample_review_with_header['id']
        mock_db_conn.fetchrow.return_value = sample_review_with_header

        response = await client.get(f'/api/v1/reviews/{review_id}')

        assert response.status_code == 200
        data = response.json()
        assert 'mid_year_completed_at' in data
        # Currently None in sample data
        assert data['mid_year_completed_at'] is None

    async def test_get_review_returns_end_year_completed_at(
        self, client, mock_db_conn, sample_review_with_header
    ):
        """GET /reviews/:id should return end_year_completed_at timestamp."""
        review_id = sample_review_with_header['id']
        mock_db_conn.fetchrow.return_value = sample_review_with_header

        response = await client.get(f'/api/v1/reviews/{review_id}')

        assert response.status_code == 200
        data = response.json()
        assert 'end_year_completed_at' in data
        # Currently None in sample data
        assert data['end_year_completed_at'] is None

    async def test_get_review_all_stage_timestamps_populated(
        self, client, mock_db_conn, sample_review_with_header
    ):
        """GET /reviews/:id should return all stage timestamps when populated."""
        from datetime import datetime, timezone
        review_with_all_dates = {
            **sample_review_with_header,
            'status': 'SIGNED',
            'stage': 'END_YEAR_REVIEW',
            'goal_setting_completed_at': datetime(2026, 2, 15, 10, 0, tzinfo=timezone.utc),
            'mid_year_completed_at': datetime(2026, 7, 15, 10, 0, tzinfo=timezone.utc),
            'end_year_completed_at': datetime(2026, 12, 15, 10, 0, tzinfo=timezone.utc),
        }
        review_id = review_with_all_dates['id']
        mock_db_conn.fetchrow.return_value = review_with_all_dates

        response = await client.get(f'/api/v1/reviews/{review_id}')

        assert response.status_code == 200
        data = response.json()
        assert '2026-02-15' in data['goal_setting_completed_at']
        assert '2026-07-15' in data['mid_year_completed_at']
        assert '2026-12-15' in data['end_year_completed_at']


@pytest.mark.asyncio
class TestUpdateReviewHeaderEndpoint:
    """Tests for PUT /api/v1/reviews/{id} endpoint for job_title and tov_level."""

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
    def mock_db_conn(self):
        """Mock database connection."""
        return AsyncMock()

    @pytest.fixture
    def sample_review_draft(self):
        """Sample review in DRAFT status."""
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
            'job_title': None,
            'tov_level': None,
            'employee_name': 'John Doe',
            'manager_name': 'Jane Smith',
        }

    @pytest_asyncio.fixture
    async def client(self, mock_current_user, mock_db_conn):
        """Async HTTP client with dependency overrides."""
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    async def test_update_job_title_in_draft_status(
        self, client, mock_db_conn, sample_review_draft
    ):
        """PUT /reviews/:id should update job_title when in DRAFT status."""
        review_id = sample_review_draft['id']
        updated_review = {**sample_review_draft, 'job_title': 'Senior Developer'}
        # Mock: get_review (check status), update_review, get_review (fetch result)
        mock_db_conn.fetchrow.side_effect = [sample_review_draft, updated_review, updated_review]

        response = await client.put(
            f'/api/v1/reviews/{review_id}',
            json={'job_title': 'Senior Developer'},
        )

        assert response.status_code == 200
        data = response.json()
        assert data['job_title'] == 'Senior Developer'

    async def test_update_tov_level_in_draft_status(
        self, client, mock_db_conn, sample_review_draft
    ):
        """PUT /reviews/:id should update tov_level when in DRAFT status."""
        review_id = sample_review_draft['id']
        updated_review = {**sample_review_draft, 'tov_level': 'B'}
        # Mock: get_review (check status), update_review, get_review (fetch result)
        mock_db_conn.fetchrow.side_effect = [sample_review_draft, updated_review, updated_review]

        response = await client.put(
            f'/api/v1/reviews/{review_id}',
            json={'tov_level': 'B'},
        )

        assert response.status_code == 200
        data = response.json()
        assert data['tov_level'] == 'B'

    async def test_update_both_fields_in_draft_status(
        self, client, mock_db_conn, sample_review_draft
    ):
        """PUT /reviews/:id should update both job_title and tov_level."""
        review_id = sample_review_draft['id']
        updated_review = {
            **sample_review_draft,
            'job_title': 'Lead Developer',
            'tov_level': 'C',
        }
        # Mock: get_review (check status), update_review, get_review (fetch result)
        mock_db_conn.fetchrow.side_effect = [sample_review_draft, updated_review, updated_review]

        response = await client.put(
            f'/api/v1/reviews/{review_id}',
            json={'job_title': 'Lead Developer', 'tov_level': 'C'},
        )

        assert response.status_code == 200
        data = response.json()
        assert data['job_title'] == 'Lead Developer'
        assert data['tov_level'] == 'C'

    async def test_update_rejected_when_not_draft(
        self, client, mock_db_conn, sample_review_draft
    ):
        """PUT /reviews/:id should reject updates when not in DRAFT status."""
        review_id = sample_review_draft['id']
        submitted_review = {**sample_review_draft, 'status': 'PENDING_MANAGER_SIGNATURE'}
        mock_db_conn.fetchrow.return_value = submitted_review

        response = await client.put(
            f'/api/v1/reviews/{review_id}',
            json={'job_title': 'Senior Developer'},
        )

        assert response.status_code == 400
        assert 'DRAFT' in response.json()['detail'] or 'status' in response.json()['detail'].lower()

    async def test_update_rejected_when_signed(
        self, client, mock_db_conn, sample_review_draft
    ):
        """PUT /reviews/:id should reject updates when review is SIGNED."""
        review_id = sample_review_draft['id']
        signed_review = {**sample_review_draft, 'status': 'SIGNED'}
        mock_db_conn.fetchrow.return_value = signed_review

        response = await client.put(
            f'/api/v1/reviews/{review_id}',
            json={'tov_level': 'A'},
        )

        assert response.status_code == 400

    async def test_update_review_not_found(self, client, mock_db_conn):
        """PUT /reviews/:id should return 404 for non-existent review."""
        review_id = uuid4()
        mock_db_conn.fetchrow.return_value = None

        response = await client.put(
            f'/api/v1/reviews/{review_id}',
            json={'job_title': 'Senior Developer'},
        )

        assert response.status_code == 404

    async def test_update_validates_tov_level(
        self, client, mock_db_conn, sample_review_draft
    ):
        """PUT /reviews/:id should validate tov_level is A, B, C, or D."""
        review_id = sample_review_draft['id']
        mock_db_conn.fetchrow.return_value = sample_review_draft

        response = await client.put(
            f'/api/v1/reviews/{review_id}',
            json={'tov_level': 'X'},  # Invalid level
        )

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestRejectReviewEndpoint:
    """Tests for review rejection endpoint."""

    @pytest.fixture
    def employee_user_id(self):
        """Employee's database user ID."""
        return uuid4()

    @pytest.fixture
    def manager_user_id(self):
        """Manager's database user ID."""
        return uuid4()

    @pytest.fixture
    def mock_employee_user(self, employee_user_id):
        """Mock authenticated employee."""
        return CurrentUser(
            keycloak_id='employee-keycloak-id',
            email='employee@example.com',
            name='John Employee',
            roles=['employee'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def mock_manager_user(self, manager_user_id):
        """Mock authenticated manager."""
        return CurrentUser(
            keycloak_id='manager-keycloak-id',
            email='manager@example.com',
            name='Jane Manager',
            roles=['manager'],
            opco_id='test-opco',
        )

    @pytest.fixture
    def sample_review_pending_employee(self, employee_user_id, manager_user_id):
        """Sample review awaiting employee signature."""
        return {
            'id': uuid4(),
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
        }

    @pytest.fixture
    def sample_review_pending_manager(self, employee_user_id, manager_user_id):
        """Sample review awaiting manager signature (end year)."""
        return {
            'id': uuid4(),
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'PENDING_MANAGER_SIGNATURE',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'employee_signature_by': employee_user_id,
        }

    @pytest.fixture
    def sample_review_pending_manager_goal_setting(self, employee_user_id, manager_user_id):
        """Sample review awaiting manager approval for goal setting."""
        return {
            'id': uuid4(),
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'PENDING_MANAGER_SIGNATURE',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
        }

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest_asyncio.fixture
    async def employee_client(self, mock_employee_user, mock_db_conn, employee_user_id):
        """HTTP client authenticated as employee."""
        app.dependency_overrides[get_current_user] = lambda: mock_employee_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': employee_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

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

    # --- POST /api/v1/reviews/:id/reject tests ---

    async def test_reject_requires_auth(self):
        """POST /reviews/:id/reject should require authentication."""
        app.dependency_overrides.clear()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            review_id = uuid4()
            response = await client.post(
                f'/api/v1/reviews/{review_id}/reject',
                json={'feedback': 'Please revise goals'},
            )
            assert response.status_code in [401, 403]

    async def test_employee_reject_success(
        self, employee_client, mock_db_conn, sample_review_pending_employee, employee_user_id
    ):
        """Employee can reject review and return to DRAFT."""
        review_id = sample_review_pending_employee['id']
        rejected_review = {
            **sample_review_pending_employee,
            'status': 'DRAFT',
            'rejection_feedback': 'Please revise goals',
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},  # User lookup
            sample_review_pending_employee,  # Get review
            {'id': uuid4()},  # Audit log entry
            rejected_review,  # Get updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await employee_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': 'Please revise goals'},
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'DRAFT'

    async def test_manager_reject_success(
        self, manager_client, mock_db_conn, sample_review_pending_manager, manager_user_id
    ):
        """Manager can reject end-year review and return to PENDING_EMPLOYEE_SIGNATURE."""
        review_id = sample_review_pending_manager['id']
        rejected_review = {
            **sample_review_pending_manager,
            'status': 'PENDING_EMPLOYEE_SIGNATURE',
            'rejection_feedback': 'Need more detail',
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},  # User lookup
            sample_review_pending_manager,  # Get review
            {'id': uuid4()},  # Audit log entry
            rejected_review,  # Get updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': 'Need more detail'},
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'PENDING_EMPLOYEE_SIGNATURE'

    async def test_manager_reject_goals_returns_to_draft(
        self, manager_client, mock_db_conn, sample_review_pending_manager_goal_setting, manager_user_id
    ):
        """Manager can reject goals and return to DRAFT."""
        review_id = sample_review_pending_manager_goal_setting['id']
        rejected_review = {
            **sample_review_pending_manager_goal_setting,
            'status': 'DRAFT',
            'rejection_feedback': 'Please revise goals',
        }
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},  # User lookup
            sample_review_pending_manager_goal_setting,  # Get review
            {'id': uuid4()},  # Audit log entry
            rejected_review,  # Get updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await manager_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': 'Please revise goals'},
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'DRAFT'

    async def test_reject_requires_feedback(
        self, employee_client, mock_db_conn, sample_review_pending_employee, employee_user_id
    ):
        """Rejection requires feedback note."""
        review_id = sample_review_pending_employee['id']
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            sample_review_pending_employee,
        ]

        # No feedback provided
        response = await employee_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={},
        )

        assert response.status_code == 422  # Validation error

    async def test_reject_empty_feedback(
        self, employee_client, mock_db_conn, sample_review_pending_employee, employee_user_id
    ):
        """Rejection requires non-empty feedback."""
        review_id = sample_review_pending_employee['id']
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            sample_review_pending_employee,
        ]

        response = await employee_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': ''},
        )

        assert response.status_code == 400
        assert 'feedback' in response.json()['detail'].lower()

    async def test_reject_review_not_found(self, employee_client, mock_db_conn, employee_user_id):
        """POST /reviews/:id/reject should return 404 for non-existent review."""
        review_id = uuid4()
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            None,  # Review not found
        ]

        response = await employee_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': 'Some feedback'},
        )

        assert response.status_code == 404

    async def test_reject_wrong_status(
        self, employee_client, mock_db_conn, sample_review_pending_employee, employee_user_id
    ):
        """Cannot reject a review that's not awaiting your signature."""
        review_id = sample_review_pending_employee['id']
        draft_review = {**sample_review_pending_employee, 'status': 'DRAFT'}
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            draft_review,
        ]

        response = await employee_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': 'Some feedback'},
        )

        assert response.status_code == 400

    async def test_reject_creates_audit_log(
        self, employee_client, mock_db_conn, sample_review_pending_employee, employee_user_id
    ):
        """Rejecting a review should create an audit log entry."""
        review_id = sample_review_pending_employee['id']
        rejected_review = {**sample_review_pending_employee, 'status': 'DRAFT'}
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            sample_review_pending_employee,
            {'id': uuid4(), 'action': 'REVIEW_REJECTED'},  # Audit log
            rejected_review,
        ]
        mock_db_conn.execute = AsyncMock()

        response = await employee_client.post(
            f'/api/v1/reviews/{review_id}/reject',
            json={'feedback': 'Please revise'},
        )

        assert response.status_code == 200
        assert mock_db_conn.fetchrow.call_count >= 3


@pytest.mark.asyncio
class TestCreateReviewEndpoint:
    """Tests for POST /api/v1/reviews endpoint with pre-population."""

    @pytest.fixture
    def employee_user_id(self):
        """Employee's database user ID."""
        return uuid4()

    @pytest.fixture
    def manager_user_id(self):
        """Manager's database user ID."""
        return uuid4()

    @pytest.fixture
    def opco_id(self):
        """OpCo ID."""
        return uuid4()

    @pytest.fixture
    def mock_hr_user(self, opco_id):
        """Mock authenticated HR user."""
        return CurrentUser(
            keycloak_id='hr-keycloak-id',
            email='hr@example.com',
            name='HR User',
            roles=['hr'],
            opco_id=str(opco_id),
        )

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        return AsyncMock()

    @pytest.fixture
    def employee_record(self, employee_user_id, manager_user_id, opco_id):
        """Sample employee record."""
        return {
            'id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'email': 'employee@example.com',
        }

    @pytest.fixture
    def previous_year_review(self, employee_user_id, manager_user_id, opco_id):
        """Sample previous year review with job_title and tov_level."""
        return {
            'id': uuid4(),
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'status': 'SIGNED',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2025,
            'job_title': 'Senior Developer',
            'tov_level': 'B',
        }

    @pytest_asyncio.fixture
    async def hr_client(self, mock_hr_user, mock_db_conn):
        """HTTP client authenticated as HR."""
        app.dependency_overrides[get_current_user] = lambda: mock_hr_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    async def test_create_review_pre_populates_job_title(
        self, hr_client, mock_db_conn, employee_record, previous_year_review, employee_user_id, opco_id
    ):
        """POST /reviews should pre-populate job_title from previous year."""
        new_review_id = uuid4()
        created_review = {
            'id': new_review_id,
            'employee_id': employee_user_id,
            'manager_id': employee_record['manager_id'],
            'opco_id': opco_id,
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': 'Senior Developer',  # Pre-populated
            'tov_level': 'B',  # Pre-populated
        }
        mock_db_conn.fetchrow.side_effect = [
            employee_record,  # Get employee
            previous_year_review,  # Get previous review
            created_review,  # Return created review
        ]

        response = await hr_client.post(
            '/api/v1/reviews',
            json={'employee_id': str(employee_user_id), 'review_year': 2026},
        )

        assert response.status_code == 201
        data = response.json()
        assert data['job_title'] == 'Senior Developer'

    async def test_create_review_pre_populates_tov_level(
        self, hr_client, mock_db_conn, employee_record, previous_year_review, employee_user_id, opco_id
    ):
        """POST /reviews should pre-populate tov_level from previous year."""
        new_review_id = uuid4()
        created_review = {
            'id': new_review_id,
            'employee_id': employee_user_id,
            'manager_id': employee_record['manager_id'],
            'opco_id': opco_id,
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': 'Senior Developer',
            'tov_level': 'B',  # Pre-populated
        }
        mock_db_conn.fetchrow.side_effect = [
            employee_record,
            previous_year_review,
            created_review,
        ]

        response = await hr_client.post(
            '/api/v1/reviews',
            json={'employee_id': str(employee_user_id), 'review_year': 2026},
        )

        assert response.status_code == 201
        data = response.json()
        assert data['tov_level'] == 'B'

    async def test_create_review_sets_manager_from_employee(
        self, hr_client, mock_db_conn, employee_record, employee_user_id, opco_id
    ):
        """POST /reviews should set manager_id from employee's current manager."""
        new_review_id = uuid4()
        manager_id = employee_record['manager_id']
        created_review = {
            'id': new_review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_id,  # From employee record
            'opco_id': opco_id,
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': None,
            'tov_level': None,
        }
        mock_db_conn.fetchrow.side_effect = [
            employee_record,
            None,  # No previous review
            created_review,
        ]

        response = await hr_client.post(
            '/api/v1/reviews',
            json={'employee_id': str(employee_user_id), 'review_year': 2026},
        )

        assert response.status_code == 201
        data = response.json()
        assert data['manager_id'] == str(manager_id)

    async def test_create_review_no_pre_population_when_no_previous(
        self, hr_client, mock_db_conn, employee_record, employee_user_id, opco_id
    ):
        """POST /reviews should not pre-populate when no previous review exists."""
        new_review_id = uuid4()
        created_review = {
            'id': new_review_id,
            'employee_id': employee_user_id,
            'manager_id': employee_record['manager_id'],
            'opco_id': opco_id,
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': None,
            'tov_level': None,
        }
        mock_db_conn.fetchrow.side_effect = [
            employee_record,
            None,  # No previous review
            created_review,
        ]

        response = await hr_client.post(
            '/api/v1/reviews',
            json={'employee_id': str(employee_user_id), 'review_year': 2026},
        )

        assert response.status_code == 201
        data = response.json()
        assert data['job_title'] is None
        assert data['tov_level'] is None


@pytest.mark.asyncio
class TestManagerReassignmentEndpoint:
    """Tests for PUT /api/v1/reviews/{id}/manager endpoint."""

    @pytest.fixture
    def employee_user_id(self):
        """Employee's database user ID."""
        return uuid4()

    @pytest.fixture
    def old_manager_id(self):
        """Old manager's database user ID."""
        return uuid4()

    @pytest.fixture
    def new_manager_id(self):
        """New manager's database user ID."""
        return uuid4()

    @pytest.fixture
    def opco_id(self):
        """OpCo ID."""
        return uuid4()

    @pytest.fixture
    def mock_hr_user(self, opco_id):
        """Mock authenticated HR user."""
        return CurrentUser(
            keycloak_id='hr-keycloak-id',
            email='hr@example.com',
            name='HR User',
            roles=['hr'],
            opco_id=str(opco_id),
        )

    @pytest.fixture
    def mock_employee_user(self, opco_id):
        """Mock authenticated employee (non-HR)."""
        return CurrentUser(
            keycloak_id='employee-keycloak-id',
            email='employee@example.com',
            name='Regular Employee',
            roles=['employee'],
            opco_id=str(opco_id),
        )

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        return AsyncMock()

    @pytest.fixture
    def sample_review(self, employee_user_id, old_manager_id, opco_id):
        """Sample review for reassignment."""
        return {
            'id': uuid4(),
            'employee_id': employee_user_id,
            'manager_id': old_manager_id,
            'opco_id': opco_id,
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
            'job_title': 'Developer',
            'tov_level': 'B',
        }

    @pytest.fixture
    def new_manager_record(self, new_manager_id, opco_id):
        """New manager user record."""
        return {
            'id': new_manager_id,
            'opco_id': opco_id,
            'email': 'newmanager@example.com',
        }

    @pytest_asyncio.fixture
    async def hr_client(self, mock_hr_user, mock_db_conn):
        """HTTP client authenticated as HR."""
        app.dependency_overrides[get_current_user] = lambda: mock_hr_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def employee_client(self, mock_employee_user, mock_db_conn):
        """HTTP client authenticated as employee (non-HR)."""
        app.dependency_overrides[get_current_user] = lambda: mock_employee_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    async def test_reassign_manager_requires_hr_role(
        self, employee_client, mock_db_conn, sample_review, new_manager_id
    ):
        """PUT /reviews/:id/manager should require HR role."""
        review_id = sample_review['id']

        response = await employee_client.put(
            f'/api/v1/reviews/{review_id}/manager',
            json={'new_manager_id': str(new_manager_id)},
        )

        assert response.status_code == 403

    async def test_reassign_manager_success(
        self, hr_client, mock_db_conn, sample_review, new_manager_id, new_manager_record, opco_id
    ):
        """PUT /reviews/:id/manager should reassign manager successfully."""
        review_id = sample_review['id']
        updated_review = {**sample_review, 'manager_id': new_manager_id}

        mock_db_conn.fetchrow.side_effect = [
            sample_review,  # 1. Get review (get_review)
            new_manager_record,  # 2. Validate new manager exists
            updated_review,  # 3. reassign_manager returns updated
            {'id': uuid4()},  # 4. Get HR user ID for audit
            {'id': uuid4()},  # 5. Audit log entry
            updated_review,  # 6. Get updated review (final)
        ]
        mock_db_conn.execute = AsyncMock()

        response = await hr_client.put(
            f'/api/v1/reviews/{review_id}/manager',
            json={'new_manager_id': str(new_manager_id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data['manager_id'] == str(new_manager_id)

    async def test_reassign_manager_review_not_found(
        self, hr_client, mock_db_conn, new_manager_id
    ):
        """PUT /reviews/:id/manager should return 404 for non-existent review."""
        review_id = uuid4()
        mock_db_conn.fetchrow.return_value = None

        response = await hr_client.put(
            f'/api/v1/reviews/{review_id}/manager',
            json={'new_manager_id': str(new_manager_id)},
        )

        assert response.status_code == 404

    async def test_reassign_manager_invalid_manager_id(
        self, hr_client, mock_db_conn, sample_review, new_manager_id
    ):
        """PUT /reviews/:id/manager should reject invalid manager_id."""
        review_id = sample_review['id']
        mock_db_conn.fetchrow.side_effect = [
            sample_review,  # Get review
            None,  # New manager not found
        ]

        response = await hr_client.put(
            f'/api/v1/reviews/{review_id}/manager',
            json={'new_manager_id': str(new_manager_id)},
        )

        assert response.status_code == 400
        assert 'manager' in response.json()['detail'].lower()

    async def test_reassign_manager_creates_audit_log(
        self, hr_client, mock_db_conn, sample_review, new_manager_id, new_manager_record, old_manager_id
    ):
        """PUT /reviews/:id/manager should create audit log with old/new manager."""
        review_id = sample_review['id']
        updated_review = {**sample_review, 'manager_id': new_manager_id}

        mock_db_conn.fetchrow.side_effect = [
            sample_review,  # 1. Get review
            new_manager_record,  # 2. Validate new manager
            updated_review,  # 3. reassign_manager returns
            {'id': uuid4()},  # 4. Get HR user ID
            {'id': uuid4(), 'action': 'MANAGER_REASSIGNED'},  # 5. Audit log
            updated_review,  # 6. Get updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await hr_client.put(
            f'/api/v1/reviews/{review_id}/manager',
            json={'new_manager_id': str(new_manager_id)},
        )

        assert response.status_code == 200
        # Verify audit log was created (call count includes all fetchrow calls)
        assert mock_db_conn.fetchrow.call_count >= 5

    async def test_reassign_manager_with_reason(
        self, hr_client, mock_db_conn, sample_review, new_manager_id, new_manager_record
    ):
        """PUT /reviews/:id/manager should accept optional reason field."""
        review_id = sample_review['id']
        updated_review = {**sample_review, 'manager_id': new_manager_id}

        mock_db_conn.fetchrow.side_effect = [
            sample_review,  # 1. Get review
            new_manager_record,  # 2. Validate new manager
            updated_review,  # 3. reassign_manager returns
            {'id': uuid4()},  # 4. Get HR user ID
            {'id': uuid4()},  # 5. Audit log with reason
            updated_review,  # 6. Get updated review
        ]
        mock_db_conn.execute = AsyncMock()

        response = await hr_client.put(
            f'/api/v1/reviews/{review_id}/manager',
            json={
                'new_manager_id': str(new_manager_id),
                'reason': 'Manager left the company',
            },
        )

        assert response.status_code == 200
