# Specification: 9-Grid Display & Calibration

## Overview

This track implements the 9-Grid performance visualization system for TSS PPM v3.0. The 9-Grid is a 3×3 matrix that combines WHAT-axis (Goals) scores with HOW-axis (Competencies) scores to provide a holistic view of employee performance. This includes real-time visualization during scoring, team overview dashboards, and HR calibration session management.

## Functional Requirements

### FR-1: 9-Grid Component

#### FR-1.1: Grid Visualization
- Display a 3×3 grid with WHAT scores on the Y-axis (rows) and HOW scores on the X-axis (columns)
- Each axis has 3 positions: 1 (Below), 2 (Meets), 3 (Exceeds)
- Grid cells use the four-color scheme:
  - **Red** (#dc2626): Position (1,1) - Low WHAT + Low HOW
  - **Orange** (#f97316): Positions (1,2), (2,1) - One low score
  - **Green** (#22c55e): Positions (1,3), (2,2), (3,1), (2,3), (3,2) - Medium to good combinations
  - **Dark Green** (#15803d): Position (3,3) - High WHAT + High HOW
- Display axis labels: "Below Expectations", "Meets Expectations", "Exceeds Expectations"

#### FR-1.2: Position Marker
- Show a circular marker indicating the employee's current position
- Position calculated from WHAT score (Y) and HOW score (X)
- Marker should be clearly visible against all cell background colors
- When scores are incomplete, show marker in a "pending" state or hide

#### FR-1.3: VETO Indicator
- When VETO is active (any competency or SCF goal scored 1), display visual warning
- VETO forces the respective axis to position 1 regardless of average
- Show red border or warning icon on the grid when VETO is triggered
- Display tooltip explaining the VETO condition

### FR-2: Manager Scoring View Integration

#### FR-2.1: 9-Grid Section
- Add a dedicated 9-Grid section to the manager's review scoring page
- Position the grid prominently (suggested: right side or below scoring panels)
- Grid updates in real-time as WHAT and HOW scores change

#### FR-2.2: Score Binding
- Receive WHAT score updates from goal scoring component
- Receive HOW score updates from competency scoring component (already emits `how-score-change`)
- Recalculate grid position whenever either score changes
- Handle incomplete scoring states gracefully

### FR-3: Team Dashboard 9-Grid

#### FR-3.1: Team Overview Grid
- Display a 9-Grid showing all team members' positions
- Each employee represented as a dot/marker on the grid
- Multiple employees in the same cell should be visually distinguishable (stacked, offset, or grouped)

#### FR-3.2: Employee Interaction
- Hover on employee marker shows tooltip with:
  - Employee name
  - WHAT score and HOW score
  - Review status (Draft, Pending Signature, Signed, etc.)
- Click on employee marker navigates to their individual review

#### FR-3.3: Distribution Statistics
- Display count of employees in each grid cell
- Show as overlay numbers or in a summary panel
- Optional: Show percentage distribution

### FR-4: HR Calibration Sessions

#### FR-4.1: Session Management
- HR can create new calibration sessions with:
  - Session name/title
  - Description/purpose
  - Target review cycle (e.g., "2026 End-Year")
  - List of reviews to include (filter by team, department, or manual selection)
  - Invited participants (managers, HR colleagues)
  - Scheduled date/time (optional)
- HR can edit and delete draft sessions
- List view of all calibration sessions with status filters

#### FR-4.2: Session Status Workflow
- **Draft**: Session created, reviews can be added/removed, not visible to participants
- **In Progress**: Session active, participants can view and discuss, scores can be adjusted
- **Completed**: Session finalized, no further changes allowed, results archived

#### FR-4.3: Calibration 9-Grid View
- Display all included employees on a single 9-Grid
- Employee markers with hover details (name, manager, current scores)
- Click marker to open detail panel (not navigate away)
- Visual grouping or color coding by team/department (optional enhancement)

#### FR-4.4: Score Adjustment
- Authorized users (HR, session owner) can adjust WHAT and/or HOW scores
- Adjustment interface shows current score and allows new score entry
- All adjustments logged to audit trail:
  - Original score
  - New score
  - User who made the change
  - Timestamp
  - Rationale (required)

#### FR-4.5: Calibration Notes
- Session-level notes for overall discussion points
- Per-employee notes for specific feedback or decisions
- Notes visible to all session participants
- Notes preserved after session completion

### FR-5: API Endpoints

#### FR-5.1: Calibration Session Endpoints
- `POST /api/v1/calibration-sessions` - Create new session
- `GET /api/v1/calibration-sessions` - List sessions (with filters)
- `GET /api/v1/calibration-sessions/{id}` - Get session details
- `PUT /api/v1/calibration-sessions/{id}` - Update session
- `DELETE /api/v1/calibration-sessions/{id}` - Delete draft session
- `POST /api/v1/calibration-sessions/{id}/start` - Move to In Progress
- `POST /api/v1/calibration-sessions/{id}/complete` - Move to Completed

#### FR-5.2: Calibration Review Endpoints
- `GET /api/v1/calibration-sessions/{id}/reviews` - Get reviews in session with scores
- `PUT /api/v1/calibration-sessions/{id}/reviews/{reviewId}/scores` - Adjust scores
- `POST /api/v1/calibration-sessions/{id}/reviews/{reviewId}/notes` - Add note

#### FR-5.3: Team Dashboard Endpoints
- `GET /api/v1/manager/team/grid` - Get team members with grid positions

## Non-Functional Requirements

### NFR-1: Performance
- 9-Grid component renders within 100ms
- Real-time updates have no perceptible lag
- Team dashboard loads within 2 seconds for teams up to 50 members
- Calibration view supports up to 200 employees without degradation

### NFR-2: Accessibility
- Grid cells have sufficient color contrast (WCAG 2.1 AA)
- Keyboard navigation supported for all interactions
- Screen reader announces grid position and cell meaning
- VETO warnings announced to assistive technology

### NFR-3: Responsive Design
- Full 9-Grid on desktop (≥1200px)
- Simplified grid on tablet (768-1199px)
- Grid viewable but read-only on mobile (<768px)

### NFR-4: Security
- Calibration sessions respect OpCo data isolation
- Score adjustments require appropriate role (HR)
- Audit trail is immutable

## Acceptance Criteria

### AC-1: 9-Grid Component
- [ ] Grid displays 3×3 matrix with correct color coding
- [ ] Position marker accurately reflects WHAT/HOW scores
- [ ] Axis labels display correctly in all supported languages
- [ ] VETO indicator appears when any axis score is forced to 1

### AC-2: Manager Scoring View
- [ ] 9-Grid section visible on review scoring page
- [ ] Grid position updates in real-time as scores change
- [ ] Works correctly with incomplete scoring (before all goals/competencies scored)

### AC-3: Team Dashboard
- [ ] All team members displayed on single grid
- [ ] Hover reveals employee details
- [ ] Click navigates to employee review
- [ ] Distribution counts displayed per cell

### AC-4: Calibration Sessions
- [ ] HR can create, edit, and delete calibration sessions
- [ ] Session workflow (Draft → In Progress → Completed) functions correctly
- [ ] All selected reviews displayed on calibration grid
- [ ] Score adjustments recorded with full audit trail
- [ ] Notes can be added at session and employee level

## Out of Scope

- Printing/exporting calibration session results (future enhancement)
- Real-time multi-user collaboration during calibration (future enhancement)
- Historical 9-Grid comparisons (previous review cycles)
- Custom color scheme configuration
- Drag-and-drop employee repositioning on grid
