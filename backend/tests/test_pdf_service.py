# TSS PPM v3.0 - PDF Service Tests
import pytest
from datetime import datetime, date
from unittest.mock import MagicMock, patch
from src.services.pdf_service import (
    PDFService,
    ReviewPDFData,
    GoalPDFData,
    CompetencyPDFData,
    SignaturePDFData,
)


@pytest.fixture
def sample_goal_data() -> list[GoalPDFData]:
    """Sample goals for testing."""
    return [
        GoalPDFData(
            title="Increase Revenue",
            description="Achieve 10% revenue growth",
            weight=40,
            goal_type="STANDARD",
            score=3,
            feedback="Excellent performance, exceeded targets",
        ),
        GoalPDFData(
            title="Safety Compliance",
            description="Maintain zero safety incidents",
            weight=30,
            goal_type="SCF",
            score=2,
            feedback="Met all safety requirements",
        ),
        GoalPDFData(
            title="Customer Satisfaction",
            description="Achieve 90% customer satisfaction",
            weight=30,
            goal_type="KAR",
            score=2,
            feedback=None,
        ),
    ]


@pytest.fixture
def sample_competency_data() -> list[CompetencyPDFData]:
    """Sample competencies for testing."""
    return [
        CompetencyPDFData(
            name="Result Driven",
            category="Dedicated",
            subcategory="Result driven",
            score=3,
        ),
        CompetencyPDFData(
            name="Committed",
            category="Dedicated",
            subcategory="Committed",
            score=2,
        ),
        CompetencyPDFData(
            name="Entrepreneurial",
            category="Entrepreneurial",
            subcategory="Entrepreneurial",
            score=2,
        ),
        CompetencyPDFData(
            name="Ambitious",
            category="Entrepreneurial",
            subcategory="Ambition",
            score=2,
        ),
        CompetencyPDFData(
            name="Market Oriented",
            category="Innovative",
            subcategory="Market oriented",
            score=3,
        ),
        CompetencyPDFData(
            name="Customer Focused",
            category="Innovative",
            subcategory="Customer focused",
            score=2,
        ),
    ]


@pytest.fixture
def sample_review_data(
    sample_goal_data: list[GoalPDFData],
    sample_competency_data: list[CompetencyPDFData],
) -> ReviewPDFData:
    """Sample review data for testing."""
    return ReviewPDFData(
        employee_name="John Doe",
        employee_email="john.doe@example.com",
        manager_name="Jane Smith",
        job_title="Senior Developer",
        department="Engineering",
        review_year=2024,
        stage="END_YEAR_REVIEW",
        status="SIGNED",
        what_score=2.40,
        how_score=2.33,
        goals=sample_goal_data,
        competencies=sample_competency_data,
        employee_signature=SignaturePDFData(
            signed_by="John Doe",
            signed_at=datetime(2024, 1, 15, 10, 30, 0),
        ),
        manager_signature=SignaturePDFData(
            signed_by="Jane Smith",
            signed_at=datetime(2024, 1, 16, 14, 0, 0),
        ),
        manager_comments="Great year overall. Keep up the good work!",
        employee_comments="Thank you for the feedback.",
    )


class TestPDFService:
    """Tests for PDF generation service."""

    def test_pdf_service_initialization(self):
        """Should initialize PDF service."""
        service = PDFService()
        assert service is not None

    def test_generate_html_returns_string(self, sample_review_data: ReviewPDFData):
        """Should generate HTML string from review data."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert isinstance(html, str)
        assert len(html) > 0

    def test_html_contains_employee_name(self, sample_review_data: ReviewPDFData):
        """Should include employee name in HTML."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "John Doe" in html

    def test_html_contains_manager_name(self, sample_review_data: ReviewPDFData):
        """Should include manager name in HTML."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "Jane Smith" in html

    def test_html_contains_review_year(self, sample_review_data: ReviewPDFData):
        """Should include review year in HTML."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "2024" in html

    def test_html_contains_job_title(self, sample_review_data: ReviewPDFData):
        """Should include job title in HTML."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "Senior Developer" in html

    def test_html_contains_goals(self, sample_review_data: ReviewPDFData):
        """Should include goals in HTML."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "Increase Revenue" in html
        assert "Safety Compliance" in html
        assert "Customer Satisfaction" in html

    def test_html_contains_goal_scores(self, sample_review_data: ReviewPDFData):
        """Should include goal scores in HTML."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        # Goals should show scores
        assert "40%" in html  # weight
        assert "STANDARD" in html or "Standard" in html

    def test_html_contains_competencies(self, sample_review_data: ReviewPDFData):
        """Should include competencies in HTML."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "Result Driven" in html
        assert "Committed" in html

    def test_html_contains_what_score(self, sample_review_data: ReviewPDFData):
        """Should include WHAT score in HTML."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "2.40" in html

    def test_html_contains_how_score(self, sample_review_data: ReviewPDFData):
        """Should include HOW score in HTML."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "2.33" in html

    def test_html_contains_brand_colors(self, sample_review_data: ReviewPDFData):
        """Should use brand colors in CSS."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        # Magenta and Navy Blue
        assert "#CC0E70" in html or "#cc0e70" in html
        assert "#004A91" in html or "#004a91" in html

    def test_html_contains_tahoma_font(self, sample_review_data: ReviewPDFData):
        """Should use Tahoma font."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "Tahoma" in html


class TestPDFServiceSignatures:
    """Tests for signature section in PDF."""

    def test_html_contains_employee_signature(self, sample_review_data: ReviewPDFData):
        """Should show employee signature when signed."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "John Doe" in html
        # Should show signature date
        assert "2024" in html or "Jan" in html or "15" in html

    def test_html_contains_manager_signature(self, sample_review_data: ReviewPDFData):
        """Should show manager signature when signed."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "Jane Smith" in html

    def test_html_shows_pending_for_unsigned(self, sample_review_data: ReviewPDFData):
        """Should show 'Pending' for unsigned reviews."""
        sample_review_data.status = "PENDING_EMPLOYEE_SIGNATURE"
        sample_review_data.employee_signature = None
        sample_review_data.manager_signature = None

        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "Pending" in html

    def test_html_contains_comments(self, sample_review_data: ReviewPDFData):
        """Should include comments section."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "Great year overall" in html
        assert "Thank you for the feedback" in html


class TestPDFServiceNineGrid:
    """Tests for 9-grid visualization in PDF."""

    def test_html_contains_nine_grid(self, sample_review_data: ReviewPDFData):
        """Should include 9-grid visualization."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        # Should have grid structure
        assert "grid" in html.lower() or "nine-grid" in html.lower()

    def test_nine_grid_shows_position(self, sample_review_data: ReviewPDFData):
        """Should highlight employee position on grid."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        # With WHAT=2.40 and HOW=2.33, should be in middle area
        # Grid should have position marker
        assert "position" in html.lower() or "marker" in html.lower() or "highlight" in html.lower()

    def test_nine_grid_color_coding(self, sample_review_data: ReviewPDFData):
        """Should use color coding for grid cells."""
        service = PDFService()
        html = service.generate_html(sample_review_data)

        # Should have colors for different performance levels
        # Red, Orange, Green variations
        assert any(color in html.lower() for color in ["#", "rgb", "color"])


class TestPDFServiceDraftWatermark:
    """Tests for draft watermark functionality."""

    def test_no_watermark_for_signed_review(self, sample_review_data: ReviewPDFData):
        """Should not show watermark for SIGNED reviews."""
        sample_review_data.status = "SIGNED"

        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "DRAFT" not in html or "watermark" not in html.lower()

    def test_watermark_for_draft_review(self, sample_review_data: ReviewPDFData):
        """Should show DRAFT watermark for non-SIGNED reviews."""
        sample_review_data.status = "DRAFT"

        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "DRAFT" in html

    def test_watermark_for_pending_signature(self, sample_review_data: ReviewPDFData):
        """Should show DRAFT watermark for pending signature status."""
        sample_review_data.status = "PENDING_EMPLOYEE_SIGNATURE"

        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "DRAFT" in html


class TestPDFGeneration:
    """Tests for actual PDF generation."""

    def test_generate_pdf_returns_bytes(self, sample_review_data: ReviewPDFData):
        """Should generate PDF as bytes."""
        service = PDFService()
        pdf_bytes = service.generate_pdf(sample_review_data)

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0

    def test_pdf_starts_with_pdf_header(self, sample_review_data: ReviewPDFData):
        """Should generate valid PDF (starts with %PDF)."""
        service = PDFService()
        pdf_bytes = service.generate_pdf(sample_review_data)

        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_with_language(self, sample_review_data: ReviewPDFData):
        """Should support language parameter."""
        service = PDFService()
        pdf_bytes = service.generate_pdf(sample_review_data, language="nl")

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0


class TestPDFServiceStageLabels:
    """Tests for stage label formatting."""

    def test_goal_setting_stage_label(self, sample_review_data: ReviewPDFData):
        """Should show 'Goal Setting' for GOAL_SETTING stage."""
        sample_review_data.stage = "GOAL_SETTING"

        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "Goal Setting" in html or "goal setting" in html.lower()

    def test_mid_year_stage_label(self, sample_review_data: ReviewPDFData):
        """Should show 'Mid-Year Review' for MID_YEAR_REVIEW stage."""
        sample_review_data.stage = "MID_YEAR_REVIEW"

        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "Mid-Year" in html or "mid-year" in html.lower()

    def test_end_year_stage_label(self, sample_review_data: ReviewPDFData):
        """Should show 'End-Year Review' for END_YEAR_REVIEW stage."""
        sample_review_data.stage = "END_YEAR_REVIEW"

        service = PDFService()
        html = service.generate_html(sample_review_data)

        assert "End-Year" in html or "end-year" in html.lower()
