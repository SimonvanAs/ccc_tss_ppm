# TSS PPM v3.0 - PDF API Endpoint Tests
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.auth import get_current_user, CurrentUser
from src.database import get_db


@pytest.fixture
def review_id():
    """Generate a review ID for testing."""
    return uuid4()


@pytest.fixture
def employee_user_id():
    """Generate an employee user ID for testing."""
    return uuid4()


@pytest.fixture
def manager_user_id():
    """Generate a manager user ID for testing."""
    return uuid4()


@pytest.fixture
def opco_id():
    """Generate an OpCo ID for testing."""
    return uuid4()


@pytest.fixture
def mock_employee_user(employee_user_id, opco_id):
    """Create mock employee user."""
    return CurrentUser(
        keycloak_id=str(uuid4()),
        email='employee@example.com',
        name='John Doe',
        roles=['EMPLOYEE'],
        opco_id=str(opco_id),
    )


@pytest.fixture
def mock_manager_user(manager_user_id, opco_id):
    """Create mock manager user."""
    return CurrentUser(
        keycloak_id=str(uuid4()),
        email='manager@example.com',
        name='Jane Smith',
        roles=['MANAGER'],
        opco_id=str(opco_id),
    )


@pytest.fixture
def sample_review_row(review_id, employee_user_id, manager_user_id, opco_id):
    """Create sample review row from database."""
    return {
        'id': review_id,
        'employee_id': employee_user_id,
        'manager_id': manager_user_id,
        'opco_id': opco_id,
        'status': 'SIGNED',
        'stage': 'END_YEAR_REVIEW',
        'review_year': 2024,
        'what_score': 2.40,
        'how_score': 2.33,
        'job_title': 'Senior Developer',
        'tov_level': 'B',
        'employee_name': 'John Doe',
        'manager_name': 'Jane Smith',
        'employee_signature_date': '2024-01-15T10:30:00',
        'employee_signature_by': employee_user_id,
        'manager_signature_date': '2024-01-16T14:00:00',
        'manager_signature_by': manager_user_id,
        'manager_comments': 'Great work!',
        'employee_comments': 'Thank you.',
        'rejection_feedback': None,
    }


@pytest.fixture
def sample_goals():
    """Create sample goals."""
    return [
        {
            'id': uuid4(),
            'title': 'Increase Revenue',
            'description': 'Achieve 10% growth',
            'weight': 50,
            'goal_type': 'STANDARD',
        },
        {
            'id': uuid4(),
            'title': 'Safety Compliance',
            'description': 'Maintain safety',
            'weight': 50,
            'goal_type': 'SCF',
        },
    ]


@pytest.fixture
def sample_goal_scores(sample_goals):
    """Create sample goal scores."""
    return [
        {'goal_id': sample_goals[0]['id'], 'score': 3, 'feedback': 'Excellent'},
        {'goal_id': sample_goals[1]['id'], 'score': 2, 'feedback': None},
    ]


@pytest.fixture
def sample_competencies():
    """Create sample competencies."""
    return [
        {'id': uuid4(), 'name': 'Result Driven', 'category': 'Dedicated', 'subcategory': 'Result driven'},
        {'id': uuid4(), 'name': 'Committed', 'category': 'Dedicated', 'subcategory': 'Committed'},
        {'id': uuid4(), 'name': 'Entrepreneurial', 'category': 'Entrepreneurial', 'subcategory': 'Entrepreneurial'},
        {'id': uuid4(), 'name': 'Ambitious', 'category': 'Entrepreneurial', 'subcategory': 'Ambition'},
        {'id': uuid4(), 'name': 'Market Oriented', 'category': 'Innovative', 'subcategory': 'Market oriented'},
        {'id': uuid4(), 'name': 'Customer Focused', 'category': 'Innovative', 'subcategory': 'Customer focused'},
    ]


@pytest.fixture
def sample_competency_scores(sample_competencies):
    """Create sample competency scores."""
    return [
        {'competency_id': sample_competencies[0]['id'], 'score': 3},
        {'competency_id': sample_competencies[1]['id'], 'score': 2},
        {'competency_id': sample_competencies[2]['id'], 'score': 2},
        {'competency_id': sample_competencies[3]['id'], 'score': 2},
        {'competency_id': sample_competencies[4]['id'], 'score': 3},
        {'competency_id': sample_competencies[5]['id'], 'score': 2},
    ]


@pytest.mark.asyncio
class TestPDFEndpoint:
    """Tests for PDF generation endpoint."""

    @pytest_asyncio.fixture
    async def mock_db_conn(self):
        """Create mock database connection."""
        mock = MagicMock()
        mock.fetchrow = AsyncMock()
        mock.fetch = AsyncMock()
        mock.execute = AsyncMock()
        return mock

    @pytest_asyncio.fixture
    async def employee_client(
        self,
        mock_employee_user,
        mock_db_conn,
        employee_user_id,
    ):
        """Create test client with employee user."""
        app.dependency_overrides[get_current_user] = lambda: mock_employee_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': employee_user_id}
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac
        app.dependency_overrides.clear()

    @pytest_asyncio.fixture
    async def manager_client(
        self,
        mock_manager_user,
        mock_db_conn,
        manager_user_id,
    ):
        """Create test client with manager user."""
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': manager_user_id}
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac
        app.dependency_overrides.clear()

    async def test_get_pdf_returns_pdf_content_type(
        self,
        employee_client,
        mock_db_conn,
        sample_review_row,
        sample_goals,
        sample_goal_scores,
        sample_competencies,
        sample_competency_scores,
        review_id,
        employee_user_id,
    ):
        """Should return PDF with correct content type."""
        # Setup mock responses
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},  # User lookup
            sample_review_row,  # Get review
            {'name': 'John Doe'},  # Employee signer name
            {'name': 'Jane Smith'},  # Manager signer name
        ]
        mock_db_conn.fetch.side_effect = [
            sample_goals,  # Get goals
            sample_goal_scores,  # Get goal scores
            sample_competencies,  # Get competencies
            sample_competency_scores,  # Get competency scores
        ]

        response = await employee_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/pdf'

    async def test_get_pdf_returns_pdf_bytes(
        self,
        employee_client,
        mock_db_conn,
        sample_review_row,
        sample_goals,
        sample_goal_scores,
        sample_competencies,
        sample_competency_scores,
        review_id,
        employee_user_id,
    ):
        """Should return valid PDF bytes."""
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            sample_review_row,
            {'name': 'John Doe'},
            {'name': 'Jane Smith'},
        ]
        mock_db_conn.fetch.side_effect = [
            sample_goals,
            sample_goal_scores,
            sample_competencies,
            sample_competency_scores,
        ]

        response = await employee_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert response.status_code == 200
        assert response.content[:4] == b'%PDF'

    async def test_get_pdf_requires_authentication(self, review_id):
        """Should require authentication."""
        app.dependency_overrides.clear()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            response = await ac.get(f'/api/v1/reviews/{review_id}/pdf')

        # Should get 401 or 403
        assert response.status_code in [401, 403]

    async def test_get_pdf_review_not_found(
        self,
        employee_client,
        mock_db_conn,
        review_id,
        employee_user_id,
    ):
        """Should return 404 for non-existent review."""
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            None,  # Review not found
        ]

        response = await employee_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert response.status_code == 404

    async def test_get_pdf_employee_can_access_own_review(
        self,
        employee_client,
        mock_db_conn,
        sample_review_row,
        sample_goals,
        sample_goal_scores,
        sample_competencies,
        sample_competency_scores,
        review_id,
        employee_user_id,
    ):
        """Employee should be able to access their own review PDF."""
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            sample_review_row,
            {'name': 'John Doe'},
            {'name': 'Jane Smith'},
        ]
        mock_db_conn.fetch.side_effect = [
            sample_goals,
            sample_goal_scores,
            sample_competencies,
            sample_competency_scores,
        ]

        response = await employee_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert response.status_code == 200

    async def test_get_pdf_manager_can_access_team_review(
        self,
        manager_client,
        mock_db_conn,
        sample_review_row,
        sample_goals,
        sample_goal_scores,
        sample_competencies,
        sample_competency_scores,
        review_id,
        manager_user_id,
    ):
        """Manager should be able to access team member's review PDF."""
        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            sample_review_row,
            {'name': 'John Doe'},
            {'name': 'Jane Smith'},
        ]
        mock_db_conn.fetch.side_effect = [
            sample_goals,
            sample_goal_scores,
            sample_competencies,
            sample_competency_scores,
        ]

        response = await manager_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert response.status_code == 200

    async def test_get_pdf_with_language_parameter(
        self,
        employee_client,
        mock_db_conn,
        sample_review_row,
        sample_goals,
        sample_goal_scores,
        sample_competencies,
        sample_competency_scores,
        review_id,
        employee_user_id,
    ):
        """Should accept language parameter."""
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            sample_review_row,
            {'name': 'John Doe'},
            {'name': 'Jane Smith'},
        ]
        mock_db_conn.fetch.side_effect = [
            sample_goals,
            sample_goal_scores,
            sample_competencies,
            sample_competency_scores,
        ]

        response = await employee_client.get(f'/api/v1/reviews/{review_id}/pdf?lang=nl')

        assert response.status_code == 200

    async def test_get_pdf_sets_filename_header(
        self,
        employee_client,
        mock_db_conn,
        sample_review_row,
        sample_goals,
        sample_goal_scores,
        sample_competencies,
        sample_competency_scores,
        review_id,
        employee_user_id,
    ):
        """Should set Content-Disposition with filename."""
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            sample_review_row,
            {'name': 'John Doe'},
            {'name': 'Jane Smith'},
        ]
        mock_db_conn.fetch.side_effect = [
            sample_goals,
            sample_goal_scores,
            sample_competencies,
            sample_competency_scores,
        ]

        response = await employee_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert 'content-disposition' in response.headers
        assert 'filename=' in response.headers['content-disposition']
        assert '.pdf' in response.headers['content-disposition']

    async def test_get_pdf_draft_status(
        self,
        employee_client,
        mock_db_conn,
        sample_review_row,
        sample_goals,
        sample_goal_scores,
        sample_competencies,
        sample_competency_scores,
        review_id,
        employee_user_id,
    ):
        """Should generate PDF for draft reviews (with watermark)."""
        sample_review_row['status'] = 'DRAFT'
        sample_review_row['employee_signature_date'] = None
        sample_review_row['employee_signature_by'] = None
        sample_review_row['manager_signature_date'] = None
        sample_review_row['manager_signature_by'] = None
        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_user_id},
            sample_review_row,
        ]
        mock_db_conn.fetch.side_effect = [
            sample_goals,
            sample_goal_scores,
            sample_competencies,
            sample_competency_scores,
        ]

        response = await employee_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert response.status_code == 200
        assert response.content[:4] == b'%PDF'
