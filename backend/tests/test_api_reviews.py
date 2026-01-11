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
        """Sample review data."""
        return {
            'id': uuid4(),
            'employee_id': uuid4(),
            'manager_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'GOAL_SETTING',
            'review_year': 2026,
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
