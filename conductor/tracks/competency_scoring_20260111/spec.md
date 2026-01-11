# Specification: Competency Scoring

## Overview

This feature enables managers to score employee competencies (the HOW-axis) as part of the performance review process. The system displays the 6 competencies specific to the employee's TOV level (A/B/C/D), allows managers to score each on a 1-3 scale using clickable score cards, and calculates the HOW score in real-time. VETO rules are enforced: if any competency scores 1, the entire HOW score becomes 1.00. The 9-Grid visualization updates based on HOW score changes.

## Functional Requirements

### FR-1: Backend Competencies API (Existing Enhancement)

- **FR-1.1**: The existing `GET /api/v1/competencies?tov_level={level}` endpoint returns the 6 competencies for the specified TOV level
- **FR-1.2**: Competencies are returned with multilingual support (EN/NL/ES titles and indicators)
- **FR-1.3**: Competencies include category (Dedicated/Entrepreneurial/Innovative), subcategory, and behavioral indicators

### FR-2: Backend Score Calculation

- **FR-2.1**: Create a scoring service (`services/scoring.py`) that calculates HOW score from competency scores
- **FR-2.2**: Implement VETO rule: if any competency score = 1, HOW score = 1.00
- **FR-2.3**: If no VETO, HOW score = average of all 6 competency scores (rounded to 2 decimal places)
- **FR-2.4**: When scores are saved via `PUT /api/v1/reviews/{id}/scores`, recalculate and persist `how_score` and `how_veto_active` on the review
- **FR-2.5**: Update `grid_position_how` based on calculated HOW score (1.00-1.66 → 1, 1.67-2.33 → 2, 2.34-3.00 → 3)

### FR-3: Frontend CompetencyScoreCard Component

- **FR-3.1**: Display three clickable score buttons (1, 2, 3) with labels:
  - 1: "Below Expectations"
  - 2: "Meets Expectations"
  - 3: "Exceeds Expectations"
- **FR-3.2**: Visual feedback on selection (highlighted border, background color change)
- **FR-3.3**: Disabled state when scoring is not allowed (e.g., review not in correct stage)
- **FR-3.4**: Emit score change event for parent component handling

### FR-4: Frontend CompetencyList Component

- **FR-4.1**: Fetch competencies from API based on employee's TOV level
- **FR-4.2**: Display all 6 competencies grouped by category (Dedicated, Entrepreneurial, Innovative)
- **FR-4.3**: For each competency, show:
  - Competency title (translated)
  - Category/subcategory badge
  - Behavioral indicators (collapsible, expanded by default)
  - CompetencyScoreCard for scoring
  - Notes textarea with voice input support
- **FR-4.4**: Highlight competency row when score = 1 (visual VETO warning)

### FR-5: Frontend HOWScoreIndicator Component

- **FR-5.1**: Display calculated HOW score in real-time as competencies are scored
- **FR-5.2**: Show VETO warning banner when any competency = 1 (magenta/red styling)
- **FR-5.3**: Display "HOW Score: X.XX" with grid position indicator (1, 2, or 3)
- **FR-5.4**: Show incomplete state when not all 6 competencies are scored

### FR-6: Frontend Scoring Logic (useCompetencyScoring composable)

- **FR-6.1**: Calculate HOW score in real-time for immediate UI feedback
- **FR-6.2**: Implement VETO rule: any score = 1 triggers VETO and sets HOW = 1.00
- **FR-6.3**: Track which competencies are scored and show progress (X/6 complete)
- **FR-6.4**: Map HOW score to grid position for 9-Grid integration

### FR-7: 9-Grid HOW-Axis Update

- **FR-7.1**: Emit HOW score changes to parent scoring view
- **FR-7.2**: Update 9-Grid component's column (HOW axis) position based on calculated score
- **FR-7.3**: 9-Grid cell highlighting reflects combined WHAT and HOW position

### FR-8: Auto-Save Integration

- **FR-8.1**: Auto-save competency scores to backend (debounced, 1 second delay)
- **FR-8.2**: Use existing SaveIndicator component to show save status
- **FR-8.3**: Persist notes with scores

## Non-Functional Requirements

- **NFR-1**: HOW score calculation must complete within 10ms for responsive UI
- **NFR-2**: Backend score persistence must complete within 500ms
- **NFR-3**: All UI text must support i18n (EN/NL/ES)
- **NFR-4**: Competency scoring UI must be responsive for tablet use

## API Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/v1/competencies?tov_level={level}` | Get competencies for TOV level | Exists |
| GET | `/api/v1/reviews/{id}/scores` | Get all scores for a review | Exists |
| PUT | `/api/v1/reviews/{id}/scores` | Save/update scores | Exists (enhance) |

## Acceptance Criteria

- [ ] Competencies API returns 6 competencies for each TOV level (A, B, C, D)
- [ ] CompetencyScoreCard displays clickable 1-2-3 buttons with visual feedback
- [ ] CompetencyList displays all 6 competencies with scoring cards and notes
- [ ] HOW score calculates correctly as average of 6 scores
- [ ] VETO rule activates when any competency scores 1 (HOW = 1.00)
- [ ] Visual VETO warning displays prominently
- [ ] HOWScoreIndicator updates in real-time
- [ ] Scores auto-save to backend with status indicator
- [ ] Backend recalculates and persists how_score on save
- [ ] 9-Grid HOW axis updates based on competency scores
- [ ] All UI supports EN/NL/ES translations
- [ ] Unit tests achieve >80% code coverage

## Out of Scope

- Employee self-scoring of competencies (employees view scores, not enter them)
- Competency framework customization by HR (admin feature)
- Calibration adjustments to competency scores (separate track)
- Mid-year vs end-year competency score comparison
- Competency score history/audit trail display
