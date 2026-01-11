# Specification: Manager Goal Scoring

## Overview

This feature enables managers to score their team members' performance reviews using the TSS PPM 9-Grid scoring system. Managers access scoring through a Team Dashboard, where they can select team members and score both the WHAT-axis (Goals) and HOW-axis (Competencies) using an intuitive clickable score card interface with real-time visual feedback.

## Functional Requirements

### FR-1: Team Dashboard

- **FR-1.1**: Display a list of team members assigned to the logged-in manager
- **FR-1.2**: Show each team member's name, current review stage, and scoring status (Not Started / In Progress / Complete)
- **FR-1.3**: Clicking a team member opens their review scoring page
- **FR-1.4**: Filter/sort options for team members (by name, status, stage)

### FR-2: WHAT-Axis Scoring (Goals)

- **FR-2.1**: Display all employee goals with their descriptions, types (Standard/KAR/SCF), and weights
- **FR-2.2**: For each goal, show three clickable score cards (1, 2, 3) with labels:
  - 1: "Below Expectations"
  - 2: "Meets Expectations"
  - 3: "Exceeds Expectations"
- **FR-2.3**: Visual feedback on card selection (highlight, border color change)
- **FR-2.4**: Calculate weighted WHAT score in real-time as scores are entered
- **FR-2.5**: Text area with voice input for written feedback per goal

### FR-3: HOW-Axis Scoring (Competencies)

- **FR-3.1**: Display the 6 competencies for the employee's TOV level (A/B/C/D)
- **FR-3.2**: Show competency name, description, and category (Dedicated/Entrepreneurial/Innovative)
- **FR-3.3**: Same clickable score card interface (1, 2, 3) for each competency
- **FR-3.4**: Calculate HOW score in real-time as scores are entered

### FR-4: VETO Rule Handling

- **FR-4.1**: Display visual warning when SCF goal is scored 1 (entire WHAT = 1.00)
- **FR-4.2**: Display visual warning when KAR goal is scored 1 (VETO triggered)
- **FR-4.3**: Show KAR compensation indicator when another KAR scores 3
- **FR-4.4**: Display visual warning when any competency is scored 1 (entire HOW = 1.00)
- **FR-4.5**: VETO warnings should be prominent but non-blocking (manager can still save)

### FR-5: Real-Time 9-Grid Visualization

- **FR-5.1**: Display 3x3 grid showing WHAT (rows) vs HOW (columns)
- **FR-5.2**: Update grid position in real-time as scores change
- **FR-5.3**: Color-code grid cells: Red, Orange, Green, Dark Green per requirements
- **FR-5.4**: Highlight current employee position on the grid
- **FR-5.5**: Show calculated WHAT and HOW scores alongside the grid

### FR-6: Auto-Save & Persistence

- **FR-6.1**: Auto-save scores to backend as they are entered (debounced)
- **FR-6.2**: Show save status indicator (Saving... / Saved / Error)
- **FR-6.3**: Persist partial scores - manager can leave and return
- **FR-6.4**: Load existing scores when reopening a review

### FR-7: Voice Input for Feedback

- **FR-7.1**: Hold-to-dictate button on each goal feedback text area
- **FR-7.2**: Visual states: Idle (grey), Recording (magenta pulse), Processing (blue spinner), Error (red shake)
- **FR-7.3**: Append transcription to existing text
- **FR-7.4**: Support EN/NL/ES languages

### FR-8: Review Status Transitions

- **FR-8.1**: "Submit Scores" button enabled only when all goals and competencies are scored
- **FR-8.2**: Submitting scores transitions review status from DRAFT to PENDING_EMPLOYEE_SIGNATURE
- **FR-8.3**: Display confirmation dialog before status transition (action is not reversible)
- **FR-8.4**: After successful submission, redirect manager to team dashboard with success message
- **FR-8.5**: Prevent further score editing once review status is PENDING_EMPLOYEE_SIGNATURE or beyond
- **FR-8.6**: Show read-only view of scores for reviews past the scoring stage

## Non-Functional Requirements

- **NFR-1**: Scoring page must load within 2 seconds
- **NFR-2**: Auto-save must complete within 1 second of score change
- **NFR-3**: 9-Grid visualization must update within 100ms of score change
- **NFR-4**: UI must be fully responsive (mobile-friendly for tablet use)
- **NFR-5**: All UI text must support i18n (EN/NL/ES)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/manager/team` | Get manager's team members |
| GET | `/api/v1/reviews/{id}/scores` | Get existing scores for a review |
| PUT | `/api/v1/reviews/{id}/scores` | Save/update scores for a review |
| POST | `/api/v1/reviews/{id}/submit-scores` | Submit scores and transition status |
| GET | `/api/v1/competencies?tov_level={level}` | Get competencies for TOV level |

## Acceptance Criteria

- [ ] Manager can view list of their team members on dashboard
- [ ] Manager can click team member to open scoring page
- [ ] Manager can score all goals using clickable score cards (1-3)
- [ ] Manager can score all competencies using clickable score cards (1-3)
- [ ] VETO warnings display when applicable scores are entered
- [ ] 9-Grid updates in real-time as scores are entered
- [ ] Scores auto-save without manual save button
- [ ] Manager can add written feedback with voice input per goal
- [ ] Partial progress is preserved when leaving/returning
- [ ] Submit button enabled only when all scores are entered
- [ ] Submitting scores transitions review to PENDING_EMPLOYEE_SIGNATURE
- [ ] Confirmation dialog shown before status transition
- [ ] Scores become read-only after submission
- [ ] All UI supports EN/NL/ES languages

## Out of Scope

- Employee self-scoring (employees view scores, not enter them)
- Calibration session functionality (separate feature)
- PDF report generation (separate feature)
- Digital signature workflow (separate feature)
- Goal editing by manager (handled in Goal Setting track)
