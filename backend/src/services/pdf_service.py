# TSS PPM v3.0 - PDF Generation Service
"""
PDF generation service using WeasyPrint.
Generates performance review PDFs with branding, 9-grid visualization,
and signature sections.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from weasyprint import HTML, CSS
from io import BytesIO


@dataclass
class GoalPDFData:
    """Goal data for PDF rendering."""
    title: str
    description: Optional[str]
    weight: int
    goal_type: str  # STANDARD, KAR, SCF
    score: Optional[int]
    feedback: Optional[str]


@dataclass
class CompetencyPDFData:
    """Competency data for PDF rendering."""
    name: str
    category: str
    subcategory: str
    score: Optional[int]


@dataclass
class SignaturePDFData:
    """Signature data for PDF rendering."""
    signed_by: str
    signed_at: datetime


@dataclass
class ReviewPDFData:
    """Complete review data for PDF generation."""
    employee_name: str
    employee_email: str
    manager_name: str
    job_title: Optional[str]
    department: Optional[str]
    review_year: int
    stage: str  # GOAL_SETTING, MID_YEAR_REVIEW, END_YEAR_REVIEW
    status: str  # DRAFT, PENDING_*, SIGNED, etc.
    what_score: Optional[float]
    how_score: Optional[float]
    goals: list[GoalPDFData]
    competencies: list[CompetencyPDFData]
    employee_signature: Optional[SignaturePDFData]
    manager_signature: Optional[SignaturePDFData]
    manager_comments: Optional[str] = None
    employee_comments: Optional[str] = None
    rejection_feedback: Optional[str] = None


class PDFService:
    """Service for generating performance review PDFs."""

    # Brand colors
    MAGENTA = "#CC0E70"
    NAVY_BLUE = "#004A91"

    # Grid colors
    GRID_COLORS = {
        "dark_green": "#1a7f37",
        "green": "#2ea44f",
        "light_green": "#7ee787",
        "orange": "#f0883e",
        "light_orange": "#ffc942",
        "red": "#cf222e",
    }

    # Translations for all supported languages
    TRANSLATIONS = {
        "en": {
            "document_title": "Performance Review Report",
            "employee": "Employee",
            "manager": "Manager",
            "job_title": "Job Title",
            "department": "Department",
            "performance_summary": "Performance Summary",
            "what_score": "WHAT Score (Goals)",
            "how_score": "HOW Score (Competencies)",
            "grid_position": "Grid Position",
            "performance_grid": "Performance Grid",
            "what_axis": "WHAT (Goals)",
            "how_axis": "HOW (Competencies)",
            "goals_what": "Goals (WHAT)",
            "goal": "Goal",
            "type": "Type",
            "weight": "Weight",
            "score": "Score",
            "competencies_how": "Competencies (HOW)",
            "comments": "Comments",
            "manager_comments": "Manager Comments",
            "employee_comments": "Employee Comments",
            "feedback_notes": "Feedback Notes",
            "signatures": "Signatures",
            "employee_signature": "Employee Signature",
            "manager_signature": "Manager Signature",
            "pending": "Pending",
            "draft": "DRAFT",
            "stage_goal_setting": "Goal Setting",
            "stage_mid_year": "Mid-Year Review",
            "stage_end_year": "End-Year Review",
            "below": "Below",
            "meets": "Meets",
            "exceeds": "Exceeds",
        },
        "nl": {
            "document_title": "Prestatiebeoordeling Rapport",
            "employee": "Medewerker",
            "manager": "Manager",
            "job_title": "Functietitel",
            "department": "Afdeling",
            "performance_summary": "Prestatieoverzicht",
            "what_score": "WAT Score (Doelen)",
            "how_score": "HOE Score (Competenties)",
            "grid_position": "Grid Positie",
            "performance_grid": "Prestatie Grid",
            "what_axis": "WAT (Doelen)",
            "how_axis": "HOE (Competenties)",
            "goals_what": "Doelen (WAT)",
            "goal": "Doel",
            "type": "Type",
            "weight": "Weging",
            "score": "Score",
            "competencies_how": "Competenties (HOE)",
            "comments": "Opmerkingen",
            "manager_comments": "Manager Opmerkingen",
            "employee_comments": "Medewerker Opmerkingen",
            "feedback_notes": "Feedback Notities",
            "signatures": "Handtekeningen",
            "employee_signature": "Medewerker Handtekening",
            "manager_signature": "Manager Handtekening",
            "pending": "In afwachting",
            "draft": "CONCEPT",
            "stage_goal_setting": "Doelstellingen",
            "stage_mid_year": "Halfjaarlijkse Beoordeling",
            "stage_end_year": "Eindejaars Beoordeling",
            "below": "Onder",
            "meets": "Voldoet",
            "exceeds": "Boven",
        },
        "es": {
            "document_title": "Informe de Evaluación de Desempeño",
            "employee": "Empleado",
            "manager": "Gerente",
            "job_title": "Puesto",
            "department": "Departamento",
            "performance_summary": "Resumen de Desempeño",
            "what_score": "Puntuación QUÉ (Objetivos)",
            "how_score": "Puntuación CÓMO (Competencias)",
            "grid_position": "Posición en Cuadrícula",
            "performance_grid": "Cuadrícula de Desempeño",
            "what_axis": "QUÉ (Objetivos)",
            "how_axis": "CÓMO (Competencias)",
            "goals_what": "Objetivos (QUÉ)",
            "goal": "Objetivo",
            "type": "Tipo",
            "weight": "Peso",
            "score": "Puntuación",
            "competencies_how": "Competencias (CÓMO)",
            "comments": "Comentarios",
            "manager_comments": "Comentarios del Gerente",
            "employee_comments": "Comentarios del Empleado",
            "feedback_notes": "Notas de Retroalimentación",
            "signatures": "Firmas",
            "employee_signature": "Firma del Empleado",
            "manager_signature": "Firma del Gerente",
            "pending": "Pendiente",
            "draft": "BORRADOR",
            "stage_goal_setting": "Definición de Objetivos",
            "stage_mid_year": "Evaluación Semestral",
            "stage_end_year": "Evaluación Anual",
            "below": "Inferior",
            "meets": "Cumple",
            "exceeds": "Supera",
        },
    }

    def __init__(self):
        """Initialize PDF service."""
        pass

    def _t(self, key: str, language: str = "en") -> str:
        """Get translation for a key in the specified language."""
        translations = self.TRANSLATIONS.get(language, self.TRANSLATIONS["en"])
        return translations.get(key, self.TRANSLATIONS["en"].get(key, key))

    def _get_stage_label(self, stage: str, language: str = "en") -> str:
        """Get translated stage label."""
        stage_keys = {
            "GOAL_SETTING": "stage_goal_setting",
            "MID_YEAR_REVIEW": "stage_mid_year",
            "END_YEAR_REVIEW": "stage_end_year",
        }
        key = stage_keys.get(stage, stage)
        return self._t(key, language)

    def generate_html(self, data: ReviewPDFData, language: str = "en") -> str:
        """Generate HTML content for the PDF."""
        is_draft = data.status != "SIGNED"
        stage_label = self._get_stage_label(data.stage, language)

        html = f"""<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta charset="UTF-8">
    <title>{self._t("document_title", language)} - {data.employee_name}</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    {self._render_watermark(language) if is_draft else ""}

    <div class="container">
        {self._render_header(data, stage_label, language)}
        {self._render_summary(data, language)}
        {self._render_nine_grid(data, language)}
        {self._render_goals(data, language)}
        {self._render_competencies(data, language)}
        {self._render_comments(data, language)}
        {self._render_signatures(data, language)}
    </div>
</body>
</html>"""
        return html

    def generate_pdf(self, data: ReviewPDFData, language: str = "en") -> bytes:
        """Generate PDF bytes from review data."""
        html_content = self.generate_html(data, language)
        html = HTML(string=html_content)

        pdf_buffer = BytesIO()
        html.write_pdf(pdf_buffer)
        pdf_buffer.seek(0)

        return pdf_buffer.read()

    def _get_css(self) -> str:
        """Return CSS styles for the PDF."""
        return f"""
            @page {{
                size: A4;
                margin: 2cm;
                @bottom-center {{
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10px;
                    color: #666;
                }}
            }}

            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}

            body {{
                font-family: Tahoma, Geneva, sans-serif;
                font-size: 11px;
                line-height: 1.4;
                color: #333;
            }}

            .container {{
                max-width: 100%;
            }}

            /* Header */
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 3px solid {self.NAVY_BLUE};
            }}

            .header-left {{
                flex: 1;
            }}

            .header-right {{
                text-align: right;
            }}

            .company-name {{
                font-size: 20px;
                font-weight: bold;
                color: {self.NAVY_BLUE};
                margin-bottom: 5px;
            }}

            .document-title {{
                font-size: 16px;
                color: {self.MAGENTA};
                margin-bottom: 10px;
            }}

            .review-year {{
                font-size: 24px;
                font-weight: bold;
                color: {self.NAVY_BLUE};
            }}

            .stage-badge {{
                display: inline-block;
                padding: 4px 12px;
                background: {self.MAGENTA};
                color: white;
                border-radius: 4px;
                font-size: 11px;
                margin-top: 5px;
            }}

            /* Info Grid */
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
                margin-bottom: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 6px;
            }}

            .info-item {{
                display: flex;
                flex-direction: column;
            }}

            .info-label {{
                font-size: 10px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}

            .info-value {{
                font-size: 12px;
                font-weight: 500;
                color: #333;
            }}

            /* Section Headers */
            .section {{
                margin-bottom: 25px;
                page-break-inside: avoid;
            }}

            .section-title {{
                font-size: 14px;
                font-weight: bold;
                color: {self.NAVY_BLUE};
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 2px solid {self.MAGENTA};
            }}

            /* Summary Cards */
            .summary-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 15px;
                margin-bottom: 20px;
            }}

            .summary-card {{
                text-align: center;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }}

            .summary-card.highlight {{
                background: {self.NAVY_BLUE};
                color: white;
            }}

            .summary-card.highlight .score-label {{
                color: rgba(255, 255, 255, 0.8);
            }}

            .score-value {{
                font-size: 28px;
                font-weight: bold;
                color: {self.NAVY_BLUE};
            }}

            .summary-card.highlight .score-value {{
                color: white;
            }}

            .score-label {{
                font-size: 10px;
                color: #666;
                text-transform: uppercase;
                margin-top: 5px;
            }}

            /* Nine Grid */
            .nine-grid-container {{
                margin-bottom: 20px;
            }}

            .nine-grid {{
                display: grid;
                grid-template-columns: 30px repeat(3, 1fr);
                grid-template-rows: repeat(3, 50px) 30px;
                gap: 2px;
                max-width: 300px;
                margin: 0 auto;
            }}

            .grid-cell {{
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 9px;
                color: white;
                border-radius: 3px;
                position: relative;
            }}

            .grid-cell.position-marker::after {{
                content: "●";
                position: absolute;
                font-size: 16px;
                color: white;
                text-shadow: 0 0 3px rgba(0,0,0,0.5);
            }}

            .axis-label {{
                font-size: 9px;
                color: #666;
                display: flex;
                align-items: center;
                justify-content: center;
            }}

            .axis-label.y-axis {{
                writing-mode: vertical-rl;
                transform: rotate(180deg);
            }}

            /* Color classes for grid */
            .cell-dark-green {{ background: {self.GRID_COLORS['dark_green']}; }}
            .cell-green {{ background: {self.GRID_COLORS['green']}; }}
            .cell-light-green {{ background: {self.GRID_COLORS['light_green']}; }}
            .cell-orange {{ background: {self.GRID_COLORS['orange']}; }}
            .cell-light-orange {{ background: {self.GRID_COLORS['light_orange']}; }}
            .cell-red {{ background: {self.GRID_COLORS['red']}; }}

            /* Goals Table */
            .goals-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15px;
            }}

            .goals-table th,
            .goals-table td {{
                padding: 8px;
                text-align: left;
                border-bottom: 1px solid #e0e0e0;
            }}

            .goals-table th {{
                background: {self.NAVY_BLUE};
                color: white;
                font-weight: 500;
                font-size: 10px;
                text-transform: uppercase;
            }}

            .goals-table td {{
                font-size: 11px;
            }}

            .goal-type {{
                display: inline-block;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 9px;
                font-weight: 500;
            }}

            .goal-type.standard {{ background: #e0e0e0; color: #333; }}
            .goal-type.kar {{ background: #ffc942; color: #333; }}
            .goal-type.scf {{ background: {self.MAGENTA}; color: white; }}

            .score-badge {{
                display: inline-block;
                width: 24px;
                height: 24px;
                line-height: 24px;
                text-align: center;
                border-radius: 50%;
                font-weight: bold;
                color: white;
            }}

            .score-1 {{ background: {self.GRID_COLORS['red']}; }}
            .score-2 {{ background: {self.GRID_COLORS['orange']}; }}
            .score-3 {{ background: {self.GRID_COLORS['dark_green']}; }}

            /* Competencies */
            .competencies-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
            }}

            .competency-category {{
                background: #f8f9fa;
                padding: 12px;
                border-radius: 6px;
                border-left: 3px solid {self.MAGENTA};
            }}

            .category-title {{
                font-weight: bold;
                color: {self.NAVY_BLUE};
                margin-bottom: 8px;
                font-size: 11px;
            }}

            .competency-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 4px 0;
                font-size: 10px;
            }}

            /* Comments */
            .comments-section {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 15px;
            }}

            .comment-block {{
                margin-bottom: 12px;
            }}

            .comment-block:last-child {{
                margin-bottom: 0;
            }}

            .comment-label {{
                font-weight: bold;
                color: {self.NAVY_BLUE};
                font-size: 10px;
                margin-bottom: 4px;
            }}

            .comment-text {{
                font-size: 11px;
                color: #333;
                line-height: 1.5;
            }}

            /* Signatures */
            .signatures-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                margin-top: 30px;
            }}

            .signature-block {{
                border-top: 2px solid #333;
                padding-top: 10px;
            }}

            .signature-label {{
                font-size: 10px;
                color: #666;
                text-transform: uppercase;
                margin-bottom: 5px;
            }}

            .signature-name {{
                font-size: 12px;
                font-weight: bold;
                color: #333;
            }}

            .signature-date {{
                font-size: 10px;
                color: #666;
            }}

            .signature-pending {{
                color: {self.MAGENTA};
                font-style: italic;
            }}

            /* Watermark */
            .watermark {{
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) rotate(-45deg);
                font-size: 120px;
                font-weight: bold;
                color: rgba(200, 200, 200, 0.3);
                z-index: -1;
                pointer-events: none;
            }}
        """

    def _render_watermark(self, language: str = "en") -> str:
        """Render DRAFT watermark."""
        return f'<div class="watermark">{self._t("draft", language)}</div>'

    def _render_header(self, data: ReviewPDFData, stage_label: str, language: str = "en") -> str:
        """Render document header."""
        return f"""
        <div class="header">
            <div class="header-left">
                <div class="company-name">TSS PPM</div>
                <div class="document-title">{self._t("document_title", language)}</div>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">{self._t("employee", language)}</span>
                        <span class="info-value">{data.employee_name}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">{self._t("manager", language)}</span>
                        <span class="info-value">{data.manager_name}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">{self._t("job_title", language)}</span>
                        <span class="info-value">{data.job_title or "—"}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">{self._t("department", language)}</span>
                        <span class="info-value">{data.department or "—"}</span>
                    </div>
                </div>
            </div>
            <div class="header-right">
                <div class="review-year">{data.review_year}</div>
                <div class="stage-badge">{stage_label}</div>
            </div>
        </div>
        """

    def _render_summary(self, data: ReviewPDFData, language: str = "en") -> str:
        """Render score summary section."""
        what_display = f"{data.what_score:.2f}" if data.what_score is not None else "—"
        how_display = f"{data.how_score:.2f}" if data.how_score is not None else "—"

        # Calculate grid position
        grid_pos = "—"
        if data.what_score is not None and data.how_score is not None:
            grid_pos = self._get_grid_position_label(data.what_score, data.how_score, language)

        return f"""
        <div class="section">
            <div class="section-title">{self._t("performance_summary", language)}</div>
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="score-value">{what_display}</div>
                    <div class="score-label">{self._t("what_score", language)}</div>
                </div>
                <div class="summary-card">
                    <div class="score-value">{how_display}</div>
                    <div class="score-label">{self._t("how_score", language)}</div>
                </div>
                <div class="summary-card highlight">
                    <div class="score-value">{grid_pos}</div>
                    <div class="score-label">{self._t("grid_position", language)}</div>
                </div>
            </div>
        </div>
        """

    def _render_nine_grid(self, data: ReviewPDFData, language: str = "en") -> str:
        """Render 9-grid visualization."""
        # Grid color mapping (row, col) -> color class
        grid_colors = [
            ["cell-dark-green", "cell-green", "cell-light-green"],      # Row 3 (Exceeds)
            ["cell-green", "cell-light-orange", "cell-orange"],         # Row 2 (Meets)
            ["cell-light-green", "cell-orange", "cell-red"],            # Row 1 (Below)
        ]

        # Determine position
        what_row, how_col = self._get_grid_position(data.what_score, data.how_score)

        cells_html = ""
        for row in range(3):
            # Y-axis label
            row_labels = ["3", "2", "1"]
            cells_html += f'<div class="axis-label y-axis">{row_labels[row]}</div>'

            for col in range(3):
                color_class = grid_colors[row][col]
                is_position = (2 - row == what_row and col == how_col) if what_row is not None else False
                position_class = "position-marker" if is_position else ""
                cells_html += f'<div class="grid-cell {color_class} {position_class}"></div>'

        # X-axis labels
        cells_html += '<div></div>'  # Empty corner
        cells_html += '<div class="axis-label">1</div>'
        cells_html += '<div class="axis-label">2</div>'
        cells_html += '<div class="axis-label">3</div>'

        return f"""
        <div class="section nine-grid-container">
            <div class="section-title">{self._t("performance_grid", language)}</div>
            <div class="nine-grid">
                {cells_html}
            </div>
            <div style="text-align: center; margin-top: 10px;">
                <span style="font-size: 10px; color: #666;">{self._t("what_axis", language)} ↑ &nbsp;&nbsp;&nbsp; {self._t("how_axis", language)} →</span>
            </div>
        </div>
        """

    def _render_goals(self, data: ReviewPDFData, language: str = "en") -> str:
        """Render goals section."""
        rows_html = ""
        for goal in data.goals:
            score_class = f"score-{goal.score}" if goal.score else ""
            score_display = f'<span class="score-badge {score_class}">{goal.score}</span>' if goal.score else "—"

            type_class = goal.goal_type.lower()
            type_display = goal.goal_type

            feedback_html = f'<div style="font-size: 9px; color: #666; margin-top: 4px;">{goal.feedback}</div>' if goal.feedback else ""

            rows_html += f"""
            <tr>
                <td>
                    <strong>{goal.title}</strong>
                    {feedback_html}
                </td>
                <td><span class="goal-type {type_class}">{type_display}</span></td>
                <td style="text-align: center;">{goal.weight}%</td>
                <td style="text-align: center;">{score_display}</td>
            </tr>
            """

        return f"""
        <div class="section">
            <div class="section-title">{self._t("goals_what", language)}</div>
            <table class="goals-table">
                <thead>
                    <tr>
                        <th style="width: 50%;">{self._t("goal", language)}</th>
                        <th style="width: 15%;">{self._t("type", language)}</th>
                        <th style="width: 15%; text-align: center;">{self._t("weight", language)}</th>
                        <th style="width: 20%; text-align: center;">{self._t("score", language)}</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """

    def _render_competencies(self, data: ReviewPDFData, language: str = "en") -> str:
        """Render competencies section."""
        # Group by category
        categories: dict[str, list[CompetencyPDFData]] = {}
        for comp in data.competencies:
            if comp.category not in categories:
                categories[comp.category] = []
            categories[comp.category].append(comp)

        categories_html = ""
        for category, comps in categories.items():
            items_html = ""
            for comp in comps:
                score_class = f"score-{comp.score}" if comp.score else ""
                score_display = f'<span class="score-badge {score_class}" style="width: 18px; height: 18px; line-height: 18px; font-size: 10px;">{comp.score}</span>' if comp.score else "—"
                items_html += f"""
                <div class="competency-item">
                    <span>{comp.name}</span>
                    {score_display}
                </div>
                """

            categories_html += f"""
            <div class="competency-category">
                <div class="category-title">{category}</div>
                {items_html}
            </div>
            """

        return f"""
        <div class="section">
            <div class="section-title">{self._t("competencies_how", language)}</div>
            <div class="competencies-grid">
                {categories_html}
            </div>
        </div>
        """

    def _render_comments(self, data: ReviewPDFData, language: str = "en") -> str:
        """Render comments section."""
        comments_html = ""

        if data.manager_comments:
            comments_html += f"""
            <div class="comment-block">
                <div class="comment-label">{self._t("manager_comments", language)}</div>
                <div class="comment-text">{data.manager_comments}</div>
            </div>
            """

        if data.employee_comments:
            comments_html += f"""
            <div class="comment-block">
                <div class="comment-label">{self._t("employee_comments", language)}</div>
                <div class="comment-text">{data.employee_comments}</div>
            </div>
            """

        if data.rejection_feedback:
            comments_html += f"""
            <div class="comment-block">
                <div class="comment-label">{self._t("feedback_notes", language)}</div>
                <div class="comment-text">{data.rejection_feedback}</div>
            </div>
            """

        if not comments_html:
            return ""

        return f"""
        <div class="section">
            <div class="section-title">{self._t("comments", language)}</div>
            <div class="comments-section">
                {comments_html}
            </div>
        </div>
        """

    def _render_signatures(self, data: ReviewPDFData, language: str = "en") -> str:
        """Render signatures section."""
        pending_text = self._t("pending", language)

        def format_signature(sig: Optional[SignaturePDFData], label: str) -> str:
            if sig:
                date_str = sig.signed_at.strftime("%B %d, %Y at %H:%M")
                return f"""
                <div class="signature-block">
                    <div class="signature-label">{label}</div>
                    <div class="signature-name">{sig.signed_by}</div>
                    <div class="signature-date">{date_str}</div>
                </div>
                """
            else:
                return f"""
                <div class="signature-block">
                    <div class="signature-label">{label}</div>
                    <div class="signature-name signature-pending">{pending_text}</div>
                </div>
                """

        employee_sig = format_signature(data.employee_signature, self._t("employee_signature", language))
        manager_sig = format_signature(data.manager_signature, self._t("manager_signature", language))

        return f"""
        <div class="section">
            <div class="section-title">{self._t("signatures", language)}</div>
            <div class="signatures-grid">
                {employee_sig}
                {manager_sig}
            </div>
        </div>
        """

    def _get_grid_position(self, what_score: Optional[float], how_score: Optional[float]) -> tuple[Optional[int], Optional[int]]:
        """Get grid row and column from scores."""
        if what_score is None or how_score is None:
            return None, None

        # Convert scores to grid positions (0-2)
        def score_to_pos(score: float) -> int:
            if score < 1.67:
                return 0  # Below
            elif score < 2.34:
                return 1  # Meets
            else:
                return 2  # Exceeds

        return score_to_pos(what_score), score_to_pos(how_score)

    def _get_grid_position_label(self, what_score: float, how_score: float, language: str = "en") -> str:
        """Get human-readable grid position label."""
        what_row, how_col = self._get_grid_position(what_score, how_score)

        if what_row is None:
            return "—"

        row_labels = [self._t("below", language), self._t("meets", language), self._t("exceeds", language)]
        col_labels = [self._t("below", language), self._t("meets", language), self._t("exceeds", language)]

        return f"{row_labels[what_row]}/{col_labels[how_col]}"
