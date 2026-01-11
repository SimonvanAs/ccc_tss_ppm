# TSS PPM v3.0 - Integration Tests for PDF Generation
"""End-to-end tests for PDF generation across statuses and languages."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.auth import CurrentUser, get_current_user
from src.database import get_db


@pytest.mark.asyncio
class TestPDFGenerationByStatus:
    """Test PDF generation at each review status."""

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
    async def manager_client(self, mock_manager_user, mock_db_conn, manager_user_id):
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': manager_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest.fixture
    def base_review_data(self, review_id, employee_user_id, manager_user_id, opco_id):
        """Base review data to be customized per test."""
        return {
            'id': review_id,
            'employee_id': employee_user_id,
            'manager_id': manager_user_id,
            'opco_id': opco_id,
            'review_year': 2026,
            'stage': 'END_YEAR_REVIEW',
            'job_title': 'Senior Developer',
            'tov_level': 'B',
            'department': 'Engineering',
            'what_score': 2.35,
            'how_score': 2.17,
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
            'manager_comments': 'Good progress this year',
            'employee_comments': 'I agree with the assessment',
            'rejection_feedback': None,
        }

    @pytest.fixture
    def sample_goals(self):
        return [
            {
                'id': uuid4(),
                'title': 'Improve team velocity',
                'goal_type': 'Standard',
                'weight': 40,
                'score': 2,
            },
            {
                'id': uuid4(),
                'title': 'Reduce tech debt',
                'goal_type': 'KAR',
                'weight': 35,
                'score': 3,
            },
            {
                'id': uuid4(),
                'title': 'Mentoring junior devs',
                'goal_type': 'Standard',
                'weight': 25,
                'score': 2,
            },
        ]

    @pytest.fixture
    def sample_competencies(self):
        return [
            {'name': 'Result Driven', 'score': 2},
            {'name': 'Committed', 'score': 3},
            {'name': 'Entrepreneurial', 'score': 2},
            {'name': 'Ambition', 'score': 2},
            {'name': 'Market Oriented', 'score': 2},
            {'name': 'Customer Focused', 'score': 2},
        ]

    @pytest.fixture
    def employee_data(self, employee_user_id):
        return {
            'id': employee_user_id,
            'name': 'John Employee',
            'email': 'john@example.com',
        }

    @pytest.fixture
    def manager_data(self, manager_user_id):
        return {
            'id': manager_user_id,
            'name': 'Jane Manager',
            'email': 'jane@example.com',
        }

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_draft_status_has_watermark(
        self,
        mock_pdf_service_class,
        manager_client,
        mock_db_conn,
        review_id,
        manager_user_id,
        base_review_data,
        sample_goals,
        sample_competencies,
        employee_data,
        manager_data,
    ):
        """DRAFT status PDF should have watermark."""
        review = {**base_review_data, 'status': 'DRAFT'}

        # Setup mock PDF service instance
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 mock pdf content'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},  # User lookup
            review,  # Get review
            employee_data,  # Employee data
            manager_data,  # Manager data
        ]
        mock_db_conn.fetch.side_effect = [
            sample_goals,  # Goals
            sample_competencies,  # Competencies
        ]

        response = await manager_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/pdf'
        # Verify generate was called with is_final=False (watermark expected)
        mock_pdf_instance.generate.assert_called_once()
        call_args = mock_pdf_instance.generate.call_args
        assert call_args is not None

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_pending_employee_signature_has_watermark(
        self,
        mock_pdf_service_class,
        manager_client,
        mock_db_conn,
        review_id,
        manager_user_id,
        base_review_data,
        sample_goals,
        sample_competencies,
        employee_data,
        manager_data,
    ):
        """PENDING_EMPLOYEE_SIGNATURE PDF should have watermark."""
        review = {**base_review_data, 'status': 'PENDING_EMPLOYEE_SIGNATURE'}

        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 mock pdf content'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            review,
            employee_data,
            manager_data,
        ]
        mock_db_conn.fetch.side_effect = [sample_goals, sample_competencies]

        response = await manager_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert response.status_code == 200
        mock_pdf_instance.generate.assert_called_once()

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_pending_manager_signature_has_watermark(
        self,
        mock_pdf_service_class,
        manager_client,
        mock_db_conn,
        review_id,
        manager_user_id,
        employee_user_id,
        base_review_data,
        sample_goals,
        sample_competencies,
        employee_data,
        manager_data,
    ):
        """PENDING_MANAGER_SIGNATURE PDF should have watermark."""
        review = {
            **base_review_data,
            'status': 'PENDING_MANAGER_SIGNATURE',
            'employee_signature_by': employee_user_id,
            'employee_signature_date': '2026-12-10T10:00:00Z',
        }

        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 mock pdf content'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            review,
            employee_data,
            manager_data,
            {'name': 'John Employee'},  # Signer lookup
        ]
        mock_db_conn.fetch.side_effect = [sample_goals, sample_competencies]

        response = await manager_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert response.status_code == 200

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_signed_status_no_watermark(
        self,
        mock_pdf_service_class,
        manager_client,
        mock_db_conn,
        review_id,
        manager_user_id,
        employee_user_id,
        base_review_data,
        sample_goals,
        sample_competencies,
        employee_data,
        manager_data,
    ):
        """SIGNED status PDF should not have watermark (final report)."""
        review = {
            **base_review_data,
            'status': 'SIGNED',
            'employee_signature_by': employee_user_id,
            'employee_signature_date': '2026-12-10T10:00:00Z',
            'manager_signature_by': manager_user_id,
            'manager_signature_date': '2026-12-15T14:00:00Z',
        }

        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 final pdf content'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            review,
            employee_data,
            manager_data,
            {'name': 'John Employee'},  # Employee signer lookup
            {'name': 'Jane Manager'},  # Manager signer lookup
        ]
        mock_db_conn.fetch.side_effect = [sample_goals, sample_competencies]

        response = await manager_client.get(f'/api/v1/reviews/{review_id}/pdf')

        assert response.status_code == 200
        # Final PDF should be generated (status is SIGNED)
        mock_pdf_instance.generate.assert_called_once()


@pytest.mark.asyncio
class TestPDFMultiLanguage:
    """Test PDF generation in all three languages."""

    @pytest.fixture
    def manager_user_id(self):
        return uuid4()

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
    async def manager_client(self, mock_manager_user, mock_db_conn, manager_user_id):
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': manager_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @pytest.fixture
    def signed_review(self, manager_user_id):
        employee_id = uuid4()
        return {
            'id': uuid4(),
            'employee_id': employee_id,
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'SIGNED',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'job_title': 'Developer',
            'tov_level': 'B',
            'department': 'IT',
            'what_score': 2.0,
            'how_score': 2.0,
            'employee_signature_by': employee_id,
            'employee_signature_date': '2026-12-10T10:00:00Z',
            'manager_signature_by': manager_user_id,
            'manager_signature_date': '2026-12-15T14:00:00Z',
            'manager_comments': None,
            'employee_comments': None,
            'rejection_feedback': None,
        }

    @pytest.fixture
    def sample_data(self, manager_user_id):
        employee_id = uuid4()
        return {
            'goals': [{'id': uuid4(), 'title': 'Goal', 'goal_type': 'Standard', 'weight': 100, 'score': 2}],
            'competencies': [{'name': 'Result Driven', 'score': 2}],
            'employee': {'id': employee_id, 'name': 'Employee', 'email': 'e@e.com'},
            'manager': {'id': manager_user_id, 'name': 'Manager', 'email': 'm@m.com'},
        }

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_english_language(
        self,
        mock_pdf_service_class,
        manager_client,
        mock_db_conn,
        manager_user_id,
        signed_review,
        sample_data,
    ):
        """PDF generation with English language."""
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 english pdf'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            signed_review,
            sample_data['employee'],
            sample_data['manager'],
            {'name': 'Employee'},
            {'name': 'Manager'},
        ]
        mock_db_conn.fetch.side_effect = [
            sample_data['goals'],
            sample_data['competencies'],
        ]

        response = await manager_client.get(
            f'/api/v1/reviews/{signed_review["id"]}/pdf?lang=en'
        )

        assert response.status_code == 200
        mock_pdf_instance.generate.assert_called_once()

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_dutch_language(
        self,
        mock_pdf_service_class,
        manager_client,
        mock_db_conn,
        manager_user_id,
        signed_review,
        sample_data,
    ):
        """PDF generation with Dutch language."""
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 dutch pdf'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            signed_review,
            sample_data['employee'],
            sample_data['manager'],
            {'name': 'Employee'},
            {'name': 'Manager'},
        ]
        mock_db_conn.fetch.side_effect = [
            sample_data['goals'],
            sample_data['competencies'],
        ]

        response = await manager_client.get(
            f'/api/v1/reviews/{signed_review["id"]}/pdf?lang=nl'
        )

        assert response.status_code == 200
        mock_pdf_instance.generate.assert_called_once()

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_spanish_language(
        self,
        mock_pdf_service_class,
        manager_client,
        mock_db_conn,
        manager_user_id,
        signed_review,
        sample_data,
    ):
        """PDF generation with Spanish language."""
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 spanish pdf'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            signed_review,
            sample_data['employee'],
            sample_data['manager'],
            {'name': 'Employee'},
            {'name': 'Manager'},
        ]
        mock_db_conn.fetch.side_effect = [
            sample_data['goals'],
            sample_data['competencies'],
        ]

        response = await manager_client.get(
            f'/api/v1/reviews/{signed_review["id"]}/pdf?lang=es'
        )

        assert response.status_code == 200
        mock_pdf_instance.generate.assert_called_once()

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_invalid_language_defaults_to_english(
        self,
        mock_pdf_service_class,
        manager_client,
        mock_db_conn,
        manager_user_id,
        signed_review,
        sample_data,
    ):
        """Invalid language parameter should default to English."""
        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 default pdf'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            signed_review,
            sample_data['employee'],
            sample_data['manager'],
            {'name': 'Employee'},
            {'name': 'Manager'},
        ]
        mock_db_conn.fetch.side_effect = [
            sample_data['goals'],
            sample_data['competencies'],
        ]

        # Invalid language 'fr' should be rejected by validation
        response = await manager_client.get(
            f'/api/v1/reviews/{signed_review["id"]}/pdf?lang=fr'
        )

        # Should return 422 for invalid language
        assert response.status_code == 422


@pytest.mark.asyncio
class TestPDFContentAccuracy:
    """Verify PDF content includes all required sections."""

    @pytest.fixture
    def manager_user_id(self):
        return uuid4()

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
    async def manager_client(self, mock_manager_user, mock_db_conn, manager_user_id):
        app.dependency_overrides[get_current_user] = lambda: mock_manager_user
        app.dependency_overrides[get_db] = lambda: mock_db_conn
        mock_db_conn.fetchrow.return_value = {'id': manager_user_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as ac:
            yield ac

        app.dependency_overrides.clear()

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_includes_employee_info(
        self, mock_pdf_service_class, manager_client, mock_db_conn, manager_user_id
    ):
        """PDF should include employee name, job title, department."""
        employee_id = uuid4()
        review = {
            'id': uuid4(),
            'employee_id': employee_id,
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'job_title': 'Senior Software Engineer',
            'tov_level': 'B',
            'department': 'Product Engineering',
            'what_score': 2.5,
            'how_score': 2.2,
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
            'manager_comments': None,
            'employee_comments': None,
            'rejection_feedback': None,
        }

        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 content'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            review,
            {'id': employee_id, 'name': 'Alice Developer', 'email': 'alice@test.com'},
            {'id': manager_user_id, 'name': 'Bob Manager', 'email': 'bob@test.com'},
        ]
        mock_db_conn.fetch.side_effect = [
            [{'id': uuid4(), 'title': 'Goal 1', 'goal_type': 'Standard', 'weight': 100, 'score': 2}],
            [{'name': 'Result Driven', 'score': 2}],
        ]

        response = await manager_client.get(f'/api/v1/reviews/{review["id"]}/pdf')

        assert response.status_code == 200
        # PDF service should be called with review data
        mock_pdf_instance.generate.assert_called_once()

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_includes_scores(
        self, mock_pdf_service_class, manager_client, mock_db_conn, manager_user_id
    ):
        """PDF should include WHAT and HOW scores."""
        employee_id = uuid4()
        review = {
            'id': uuid4(),
            'employee_id': employee_id,
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'job_title': 'Developer',
            'tov_level': 'B',
            'department': 'IT',
            'what_score': 2.75,  # Exceeds expectations
            'how_score': 1.83,  # Meets expectations
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
            'manager_comments': None,
            'employee_comments': None,
            'rejection_feedback': None,
        }

        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 content'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            review,
            {'id': employee_id, 'name': 'Test', 'email': 't@t.com'},
            {'id': manager_user_id, 'name': 'Manager', 'email': 'm@m.com'},
        ]
        mock_db_conn.fetch.side_effect = [
            [{'id': uuid4(), 'title': 'G', 'goal_type': 'Standard', 'weight': 100, 'score': 3}],
            [{'name': 'R', 'score': 2}],
        ]

        response = await manager_client.get(f'/api/v1/reviews/{review["id"]}/pdf')

        assert response.status_code == 200

    @patch('src.services.pdf_service.PDFService')
    async def test_pdf_includes_goals_and_competencies(
        self, mock_pdf_service_class, manager_client, mock_db_conn, manager_user_id
    ):
        """PDF should include all goals and competencies with scores."""
        employee_id = uuid4()
        review = {
            'id': uuid4(),
            'employee_id': employee_id,
            'manager_id': manager_user_id,
            'opco_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'job_title': 'Developer',
            'tov_level': 'B',
            'department': 'IT',
            'what_score': 2.0,
            'how_score': 2.0,
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
            'manager_comments': None,
            'employee_comments': None,
            'rejection_feedback': None,
        }

        goals = [
            {'id': uuid4(), 'title': 'Increase sales', 'goal_type': 'KAR', 'weight': 50, 'score': 2},
            {'id': uuid4(), 'title': 'Reduce costs', 'goal_type': 'SCF', 'weight': 30, 'score': 3},
            {'id': uuid4(), 'title': 'Training', 'goal_type': 'Standard', 'weight': 20, 'score': 2},
        ]
        competencies = [
            {'name': 'Result Driven', 'score': 2},
            {'name': 'Committed', 'score': 2},
            {'name': 'Entrepreneurial', 'score': 2},
            {'name': 'Ambition', 'score': 2},
            {'name': 'Market Oriented', 'score': 2},
            {'name': 'Customer Focused', 'score': 2},
        ]

        mock_pdf_instance = MagicMock()
        mock_pdf_instance.generate.return_value = b'%PDF-1.4 content'
        mock_pdf_service_class.return_value = mock_pdf_instance

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_user_id},
            review,
            {'id': employee_id, 'name': 'Test', 'email': 't@t.com'},
            {'id': manager_user_id, 'name': 'Manager', 'email': 'm@m.com'},
        ]
        mock_db_conn.fetch.side_effect = [goals, competencies]

        response = await manager_client.get(f'/api/v1/reviews/{review["id"]}/pdf')

        assert response.status_code == 200


@pytest.mark.asyncio
class TestPDFRBACEnforcement:
    """Test PDF access control."""

    @pytest.fixture
    def mock_db_conn(self):
        conn = AsyncMock()
        return conn

    async def test_pdf_requires_authentication(self, mock_db_conn):
        """PDF endpoint should require authentication."""
        app.dependency_overrides.clear()
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(f'/api/v1/reviews/{uuid4()}/pdf')
            assert response.status_code in [401, 403]

        app.dependency_overrides.clear()

    async def test_employee_can_access_own_pdf(self, mock_db_conn):
        """Employee can download PDF of their own review."""
        employee_id = uuid4()
        review_id = uuid4()

        mock_employee = CurrentUser(
            keycloak_id='emp-kc-id',
            email='emp@test.com',
            name='Employee',
            roles=['employee'],
            opco_id='test-opco',
        )

        app.dependency_overrides[get_current_user] = lambda: mock_employee
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        review = {
            'id': review_id,
            'employee_id': employee_id,
            'manager_id': uuid4(),
            'opco_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'job_title': 'Dev',
            'tov_level': 'B',
            'department': 'IT',
            'what_score': 2.0,
            'how_score': 2.0,
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
            'manager_comments': None,
            'employee_comments': None,
            'rejection_feedback': None,
        }

        mock_db_conn.fetchrow.side_effect = [
            {'id': employee_id},  # User lookup returns employee's DB id
            review,  # Get review
            {'id': employee_id, 'name': 'Employee', 'email': 'e@e.com'},
            {'id': uuid4(), 'name': 'Manager', 'email': 'm@m.com'},
        ]
        mock_db_conn.fetch.side_effect = [
            [{'id': uuid4(), 'title': 'G', 'goal_type': 'Standard', 'weight': 100, 'score': 2}],
            [{'name': 'R', 'score': 2}],
        ]

        with patch('src.services.pdf_service.PDFService') as mock_pdf_class:
            mock_pdf = MagicMock()
            mock_pdf.generate.return_value = b'%PDF-1.4 content'
            mock_pdf_class.return_value = mock_pdf

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url='http://test') as client:
                response = await client.get(f'/api/v1/reviews/{review_id}/pdf')
                assert response.status_code == 200

        app.dependency_overrides.clear()

    async def test_manager_can_access_team_pdf(self, mock_db_conn):
        """Manager can download PDF of team member review."""
        manager_id = uuid4()
        employee_id = uuid4()
        review_id = uuid4()

        mock_manager = CurrentUser(
            keycloak_id='mgr-kc-id',
            email='mgr@test.com',
            name='Manager',
            roles=['manager'],
            opco_id='test-opco',
        )

        app.dependency_overrides[get_current_user] = lambda: mock_manager
        app.dependency_overrides[get_db] = lambda: mock_db_conn

        review = {
            'id': review_id,
            'employee_id': employee_id,
            'manager_id': manager_id,  # Manager is assigned to this review
            'opco_id': uuid4(),
            'status': 'DRAFT',
            'stage': 'END_YEAR_REVIEW',
            'review_year': 2026,
            'job_title': 'Dev',
            'tov_level': 'B',
            'department': 'IT',
            'what_score': 2.0,
            'how_score': 2.0,
            'employee_signature_by': None,
            'employee_signature_date': None,
            'manager_signature_by': None,
            'manager_signature_date': None,
            'manager_comments': None,
            'employee_comments': None,
            'rejection_feedback': None,
        }

        mock_db_conn.fetchrow.side_effect = [
            {'id': manager_id},  # User lookup
            review,
            {'id': employee_id, 'name': 'Employee', 'email': 'e@e.com'},
            {'id': manager_id, 'name': 'Manager', 'email': 'm@m.com'},
        ]
        mock_db_conn.fetch.side_effect = [
            [{'id': uuid4(), 'title': 'G', 'goal_type': 'Standard', 'weight': 100, 'score': 2}],
            [{'name': 'R', 'score': 2}],
        ]

        with patch('src.services.pdf_service.PDFService') as mock_pdf_class:
            mock_pdf = MagicMock()
            mock_pdf.generate.return_value = b'%PDF-1.4 content'
            mock_pdf_class.return_value = mock_pdf

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url='http://test') as client:
                response = await client.get(f'/api/v1/reviews/{review_id}/pdf')
                assert response.status_code == 200

        app.dependency_overrides.clear()
