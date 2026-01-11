# TSS PPM v3.0 - Calibration Score Adjustment Tests
"""Tests for calibration score adjustment API endpoints."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db


@pytest.mark.asyncio
class TestCalibrationScoreAdjustment:
    """Tests for calibration score adjustment endpoints."""

    @pytest.fixture
    def sample_opco_id(self):
        """Sample OpCo ID as UUID."""
        return uuid4()

    @pytest.fixture
    def mock_hr_user(self, sample_opco_id):
        """Mock authenticated HR user."""
        return CurrentUser(
            keycloak_id='test-hr-id',
            email='hr@example.com',
            name='HR User',
            roles=['employee', 'hr'],
            opco_id=str(sample_opco_id),
        )

    @pytest.fixture
    def mock_manager_user(self, sample_opco_id):
        """Mock authenticated manager user (not HR)."""
        return CurrentUser(
            keycloak_id='test-manager-id',
            email='manager@example.com',
            name='Test Manager',
            roles=['employee', 'manager'],
            opco_id=str(sample_opco_id),
        )

    @pytest.fixture
    def sample_session(self):
        """Sample calibration session in IN_PROGRESS status."""
        return {
            'id': uuid4(),
            'opco_id': uuid4(),
            'name': 'Q4 2026 Calibration',
            'description': 'End of year calibration session',
            'review_year': 2026,
            'scope': 'COMPANY_WIDE',
            'business_unit_id': None,
            'status': 'IN_PROGRESS',
            'facilitator_id': uuid4(),
            'created_by': uuid4(),
            'snapshot_taken_at': None,
            'completed_at': None,
            'notes': None,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }

    @pytest.fixture
    def sample_review(self):
        """Sample review with scores."""
        return {
            'id': uuid4(),
            'employee_id': uuid4(),
            'manager_id': uuid4(),
            'what_score': Decimal('2.50'),
            'how_score': Decimal('2.80'),
            'grid_position_what': 2,
            'grid_position_how': 3,
            'what_veto_active': False,
            'how_veto_active': False,
            'status': 'MANAGER_SIGNED',
        }

    @pytest.fixture
    def sample_adjustment(self, sample_session, sample_review):
        """Sample score adjustment record."""
        return {
            'id': uuid4(),
            'session_id': sample_session['id'],
            'review_id': sample_review['id'],
            'adjusted_by': uuid4(),
            'original_what_score': Decimal('2.50'),
            'original_how_score': Decimal('2.80'),
            'original_grid_what': 2,
            'original_grid_how': 3,
            'adjusted_what_score': Decimal('3.00'),
            'adjusted_how_score': Decimal('2.80'),
            'adjusted_grid_what': 3,
            'adjusted_grid_how': 3,
            'adjustment_notes': 'Adjusted based on calibration discussion',
            'created_at': datetime.now(timezone.utc),
        }

    @pytest.fixture
    def mock_db_conn(self):
        """Mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    async def hr_client(self, mock_hr_user, mock_db_conn):
        """Async HTTP client with HR authentication."""
        app.dependency_overrides[get_current_user] = lambda: mock_hr_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest.fixture
    async def manager_client(self, mock_manager_user, mock_db_conn):
        """Async HTTP client with manager authentication (not HR)."""
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    # --- Authorization Tests ---

    async def test_adjust_scores_requires_hr_role(self, manager_client, sample_session, sample_review):
        """PUT /calibration-sessions/{id}/reviews/{id}/scores should require HR role."""
        session_id = str(sample_session['id'])
        review_id = str(sample_review['id'])

        response = await manager_client.put(
            f'/api/v1/calibration-sessions/{session_id}/reviews/{review_id}/scores',
            json={
                'what_score': 3.0,
                'how_score': 2.8,
                'rationale': 'Test adjustment',
            }
        )

        assert response.status_code == 403

    # --- Score Adjustment Tests ---

    async def test_adjust_scores_success(self, hr_client, mock_db_conn, sample_session, sample_review, sample_adjustment):
        """PUT /calibration-sessions/{id}/reviews/{id}/scores should adjust scores."""
        # Mock flow:
        # 1. _get_user_id - fetchrow for user
        # 2. get_session_by_id - fetchrow for session
        # 3. is_review_in_session - fetchrow (returns row if in session)
        # 4. get_review_current_scores - fetchrow for current scores
        # 5. adjust_review_scores -> get_review_current_scores (again) - fetchrow
        # 6. adjust_review_scores -> INSERT adjustment - fetchrow
        mock_db_conn.fetchrow.side_effect = [
            {'id': uuid4()},  # _get_user_id
            sample_session,  # get_session_by_id
            {'1': 1},  # is_review_in_session returns non-None
            sample_review,   # get_review_current_scores (from router)
            sample_review,   # get_review_current_scores (from repo.adjust_review_scores)
            sample_adjustment,  # INSERT calibration_adjustments
        ]
        mock_db_conn.execute.return_value = 'UPDATE 1'

        session_id = str(sample_session['id'])
        review_id = str(sample_review['id'])

        response = await hr_client.put(
            f'/api/v1/calibration-sessions/{session_id}/reviews/{review_id}/scores',
            json={
                'what_score': 3.0,
                'how_score': 2.8,
                'rationale': 'Adjusted based on calibration discussion',
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert 'adjustment_id' in data
        assert data['what_score'] == 3.0

    async def test_adjust_scores_requires_rationale(self, hr_client, mock_db_conn, sample_session):
        """PUT /calibration-sessions/{id}/reviews/{id}/scores should require rationale."""
        mock_db_conn.fetchrow.return_value = sample_session
        session_id = str(sample_session['id'])
        review_id = str(uuid4())

        response = await hr_client.put(
            f'/api/v1/calibration-sessions/{session_id}/reviews/{review_id}/scores',
            json={
                'what_score': 3.0,
                'how_score': 2.8,
                # Missing rationale
            }
        )

        assert response.status_code == 422

    async def test_adjust_scores_session_must_be_in_progress(self, hr_client, mock_db_conn, sample_session):
        """PUT /calibration-sessions/{id}/reviews/{id}/scores should only work for IN_PROGRESS sessions."""
        sample_session['status'] = 'PREPARATION'
        mock_db_conn.fetchrow.return_value = sample_session
        session_id = str(sample_session['id'])
        review_id = str(uuid4())

        response = await hr_client.put(
            f'/api/v1/calibration-sessions/{session_id}/reviews/{review_id}/scores',
            json={
                'what_score': 3.0,
                'how_score': 2.8,
                'rationale': 'Test adjustment',
            }
        )

        assert response.status_code == 400
        assert 'IN_PROGRESS' in response.json()['detail']

    async def test_adjust_scores_session_not_found(self, hr_client, mock_db_conn):
        """PUT /calibration-sessions/{id}/reviews/{id}/scores should return 404 for missing session."""
        mock_db_conn.fetchrow.return_value = None
        session_id = str(uuid4())
        review_id = str(uuid4())

        response = await hr_client.put(
            f'/api/v1/calibration-sessions/{session_id}/reviews/{review_id}/scores',
            json={
                'what_score': 3.0,
                'how_score': 2.8,
                'rationale': 'Test adjustment',
            }
        )

        assert response.status_code == 404

    async def test_adjust_scores_review_not_in_session(self, hr_client, mock_db_conn, sample_session):
        """PUT should return 404 if review is not in the session."""
        mock_db_conn.fetchrow.side_effect = [
            sample_session,  # get_session_by_id
            None,  # get review - not found
        ]
        session_id = str(sample_session['id'])
        review_id = str(uuid4())

        response = await hr_client.put(
            f'/api/v1/calibration-sessions/{session_id}/reviews/{review_id}/scores',
            json={
                'what_score': 3.0,
                'how_score': 2.8,
                'rationale': 'Test adjustment',
            }
        )

        assert response.status_code == 404

    async def test_adjust_scores_creates_audit_trail(self, hr_client, mock_db_conn, sample_session, sample_review, sample_adjustment):
        """PUT should create an audit trail entry in calibration_adjustments."""
        # Same mock flow as test_adjust_scores_success
        mock_db_conn.fetchrow.side_effect = [
            {'id': uuid4()},  # _get_user_id
            sample_session,  # get_session_by_id
            {'1': 1},  # is_review_in_session
            sample_review,   # get_review_current_scores (from router)
            sample_review,   # get_review_current_scores (from repo)
            sample_adjustment,  # INSERT calibration_adjustments
        ]
        mock_db_conn.execute.return_value = 'UPDATE 1'

        session_id = str(sample_session['id'])
        review_id = str(sample_review['id'])

        response = await hr_client.put(
            f'/api/v1/calibration-sessions/{session_id}/reviews/{review_id}/scores',
            json={
                'what_score': 3.0,
                'how_score': 2.8,
                'rationale': 'Adjusted based on discussion',
            }
        )

        assert response.status_code == 200
        # Verify the adjustment was created with the original and new scores
        data = response.json()
        assert data['original_what_score'] == 2.5
        assert data['what_score'] == 3.0

    async def test_adjust_scores_completed_session_rejected(self, hr_client, mock_db_conn, sample_session):
        """PUT should reject adjustments on COMPLETED sessions."""
        sample_session['status'] = 'COMPLETED'
        mock_db_conn.fetchrow.return_value = sample_session
        session_id = str(sample_session['id'])
        review_id = str(uuid4())

        response = await hr_client.put(
            f'/api/v1/calibration-sessions/{session_id}/reviews/{review_id}/scores',
            json={
                'what_score': 3.0,
                'how_score': 2.8,
                'rationale': 'Test adjustment',
            }
        )

        assert response.status_code == 400

    # --- Get Adjustment History Tests ---

    async def test_get_adjustment_history(self, hr_client, mock_db_conn, sample_session, sample_adjustment):
        """GET /calibration-sessions/{id}/reviews/{id}/adjustments should return history."""
        mock_db_conn.fetchrow.return_value = sample_session
        mock_db_conn.fetch.return_value = [sample_adjustment]
        session_id = str(sample_session['id'])
        review_id = str(sample_adjustment['review_id'])

        response = await hr_client.get(
            f'/api/v1/calibration-sessions/{session_id}/reviews/{review_id}/adjustments'
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['adjustment_notes'] == 'Adjusted based on calibration discussion'


@pytest.mark.asyncio
class TestCalibrationRepository:
    """Tests for calibration score adjustment repository methods."""

    @pytest.fixture
    def mock_conn(self):
        """Create a mock database connection."""
        conn = AsyncMock()
        return conn

    @pytest.fixture
    def sample_review_id(self):
        return uuid4()

    @pytest.fixture
    def sample_session_id(self):
        return uuid4()

    async def test_adjust_review_scores_creates_audit(self, mock_conn, sample_session_id, sample_review_id):
        """adjust_review_scores should create audit trail entry."""
        from src.repositories.calibration import CalibrationRepository

        repo = CalibrationRepository(mock_conn)
        user_id = uuid4()

        # Mock the review query
        mock_conn.fetchrow.side_effect = [
            {  # Current review scores
                'id': sample_review_id,
                'what_score': Decimal('2.50'),
                'how_score': Decimal('2.80'),
                'grid_position_what': 2,
                'grid_position_how': 3,
            },
            {  # Adjustment record created
                'id': uuid4(),
                'session_id': sample_session_id,
                'review_id': sample_review_id,
                'adjusted_by': user_id,
                'original_what_score': Decimal('2.50'),
                'original_how_score': Decimal('2.80'),
                'adjusted_what_score': Decimal('3.00'),
                'adjusted_how_score': Decimal('2.80'),
                'adjustment_notes': 'Test rationale',
                'created_at': datetime.now(timezone.utc),
            },
        ]
        mock_conn.execute.return_value = 'UPDATE 1'

        result = await repo.adjust_review_scores(
            session_id=sample_session_id,
            review_id=sample_review_id,
            what_score=Decimal('3.00'),
            how_score=Decimal('2.80'),
            adjusted_by=user_id,
            rationale='Test rationale',
        )

        assert result is not None
        assert result['original_what_score'] == Decimal('2.50')
        assert result['adjusted_what_score'] == Decimal('3.00')

    async def test_get_review_adjustments(self, mock_conn, sample_session_id, sample_review_id):
        """get_review_adjustments should return adjustment history."""
        from src.repositories.calibration import CalibrationRepository

        repo = CalibrationRepository(mock_conn)

        mock_conn.fetch.return_value = [
            {
                'id': uuid4(),
                'session_id': sample_session_id,
                'review_id': sample_review_id,
                'adjusted_by': uuid4(),
                'original_what_score': Decimal('2.50'),
                'adjusted_what_score': Decimal('3.00'),
                'adjustment_notes': 'First adjustment',
                'created_at': datetime.now(timezone.utc),
                'adjuster_first_name': 'HR',
                'adjuster_last_name': 'User',
            }
        ]

        result = await repo.get_review_adjustments(sample_session_id, sample_review_id)

        assert len(result) == 1
        assert result[0]['adjustment_notes'] == 'First adjustment'
