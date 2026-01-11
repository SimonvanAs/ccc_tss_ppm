# Plan: 9-Grid Display & Calibration

## Phase 1: 9-Grid Core Component [checkpoint: 51587f1]

_Note: Phase 1 was completed as part of Manager Goal Scoring track (Phase 4)_

- [x] Task: Write tests for NineGrid component `579a419`
  - [x] Test renders 3×3 grid with correct structure
  - [x] Test cell colors follow four-color scheme
  - [x] Test position marker placement based on WHAT/HOW scores
  - [x] Test axis labels display correctly
  - [x] Test VETO indicator appears when vetoActive is true
  - [x] Test incomplete state (null scores) handling
- [x] Task: Implement NineGrid.vue component `579a419`
  - [x] Create 3×3 grid layout with CSS Grid
  - [x] Apply four-color scheme to cells
  - [x] Add position marker with dynamic positioning
  - [x] Display axis labels (numeric 1/2/3)
  - [x] Add VETO warning indicator
  - [x] Handle incomplete scoring states
- [x] Task: Add i18n translations for grid labels (EN/NL/ES) `bbc0563`
- [x] Task: Conductor - User Manual Verification 'Phase 1: 9-Grid Core Component' (Protocol in workflow.md) `51587f1`

## Phase 2: Manager Scoring View Integration [checkpoint: 591b898]

_Note: Phase 2 was completed as part of Manager Goal Scoring track (Phase 5)_

- [x] Task: Write tests for 9-Grid integration in scoring view `158bf73`
  - [x] Test NineGrid receives WHAT score from goal scoring
  - [x] Test NineGrid receives HOW score from competency scoring
  - [x] Test grid position updates on score changes
  - [x] Test VETO state propagates to grid
- [x] Task: Integrate NineGrid into manager review scoring page `158bf73`
  - [x] Add NineGrid section to scoring page layout
  - [x] Connect WHAT score from goal scoring component
  - [x] Connect HOW score from competency scoring component (use existing how-score-change event)
  - [x] Handle incomplete scoring (partial WHAT/HOW)
- [x] Task: Conductor - User Manual Verification 'Phase 2: Manager Scoring View Integration' (Protocol in workflow.md) `591b898`

## Phase 3: Team Dashboard 9-Grid

- [x] Task: Write tests for GET /api/v1/manager/team/grid endpoint
  - [x] Test returns team members with WHAT/HOW scores
  - [x] Test filters by manager_id from JWT
  - [x] Test includes review status for each member
  - [x] Test OpCo isolation
- [x] Task: Implement GET /api/v1/manager/team/grid endpoint `b0b0e84`
  - [x] Create team_grid repository function
  - [x] Create router endpoint with JWT auth
  - [x] Return employee id, name, what_score, how_score, review_status
- [x] Task: Write tests for TeamNineGrid component
  - [x] Test displays multiple employee markers
  - [x] Test hover shows employee details tooltip
  - [x] Test click emits navigation event
  - [x] Test distribution counts per cell
  - [x] Test handles overlapping positions
- [x] Task: Implement TeamNineGrid.vue component `b0b0e84`
  - [x] Extend NineGrid with multi-employee support
  - [x] Add employee markers with positioning
  - [x] Implement hover tooltip with employee details
  - [x] Add click handler for navigation
  - [x] Display distribution counts overlay
- [x] Task: Create team dashboard page with TeamNineGrid
  - [x] Fetch team data from API
  - [x] Display TeamNineGrid component
  - [x] Handle navigation to individual reviews
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Team Dashboard 9-Grid' (Protocol in workflow.md)

## Phase 4: Calibration Backend - Database & Core API

- [ ] Task: Create calibration_sessions database table
  - [ ] Define schema: id, opco_id, name, description, review_cycle, status, created_by, created_at, updated_at
  - [ ] Add status enum: draft, in_progress, completed
- [ ] Task: Create calibration_session_reviews junction table
  - [ ] Define schema: session_id, review_id, added_at
- [ ] Task: Create calibration_session_participants table
  - [ ] Define schema: session_id, user_id, role, added_at
- [ ] Task: Create calibration_score_adjustments audit table
  - [ ] Define schema: id, session_id, review_id, field (what_score/how_score), original_value, new_value, adjusted_by, rationale, adjusted_at
- [ ] Task: Create calibration_notes table
  - [ ] Define schema: id, session_id, review_id (nullable for session-level), content, created_by, created_at
- [ ] Task: Write tests for calibration sessions repository
  - [ ] Test create session
  - [ ] Test get session by id
  - [ ] Test list sessions with filters
  - [ ] Test update session
  - [ ] Test delete draft session
  - [ ] Test add/remove reviews from session
  - [ ] Test status transitions
- [ ] Task: Implement calibration sessions repository
  - [ ] Create CRUD functions for sessions
  - [ ] Implement review management functions
  - [ ] Implement status transition logic
  - [ ] Enforce OpCo isolation
- [ ] Task: Write tests for calibration session API endpoints
  - [ ] Test POST /api/v1/calibration-sessions
  - [ ] Test GET /api/v1/calibration-sessions
  - [ ] Test GET /api/v1/calibration-sessions/{id}
  - [ ] Test PUT /api/v1/calibration-sessions/{id}
  - [ ] Test DELETE /api/v1/calibration-sessions/{id}
  - [ ] Test POST /api/v1/calibration-sessions/{id}/start
  - [ ] Test POST /api/v1/calibration-sessions/{id}/complete
  - [ ] Test HR role authorization
- [ ] Task: Implement calibration session API endpoints
  - [ ] Create router with all endpoints
  - [ ] Add HR role authorization
  - [ ] Implement request/response schemas
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Calibration Backend - Database & Core API' (Protocol in workflow.md)

## Phase 5: Calibration Backend - Reviews & Score Adjustments

- [ ] Task: Write tests for calibration reviews endpoints
  - [ ] Test GET /api/v1/calibration-sessions/{id}/reviews
  - [ ] Test returns reviews with current scores
  - [ ] Test includes employee and manager info
- [ ] Task: Implement GET /api/v1/calibration-sessions/{id}/reviews endpoint
  - [ ] Join reviews with scores and user info
  - [ ] Return data needed for calibration grid
- [ ] Task: Write tests for score adjustment endpoint
  - [ ] Test PUT /api/v1/calibration-sessions/{id}/reviews/{reviewId}/scores
  - [ ] Test creates audit trail entry
  - [ ] Test requires rationale
  - [ ] Test updates review scores
  - [ ] Test only works for in_progress sessions
- [ ] Task: Implement score adjustment endpoint
  - [ ] Validate session is in_progress
  - [ ] Update review scores
  - [ ] Create audit trail entry
  - [ ] Require rationale field
- [ ] Task: Write tests for calibration notes endpoints
  - [ ] Test POST /api/v1/calibration-sessions/{id}/notes (session-level)
  - [ ] Test POST /api/v1/calibration-sessions/{id}/reviews/{reviewId}/notes
  - [ ] Test GET notes for session
- [ ] Task: Implement calibration notes endpoints
  - [ ] Create/read notes at session level
  - [ ] Create/read notes at review level
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Calibration Backend - Reviews & Score Adjustments' (Protocol in workflow.md)

## Phase 6: Calibration Frontend - Session Management

- [ ] Task: Write tests for CalibrationSessionList component
  - [ ] Test displays list of sessions
  - [ ] Test shows session status badges
  - [ ] Test filter by status works
  - [ ] Test create new session button
- [ ] Task: Implement CalibrationSessionList.vue component
  - [ ] Fetch sessions from API
  - [ ] Display in table/card format
  - [ ] Add status filter
  - [ ] Add create session button
- [ ] Task: Write tests for CalibrationSessionForm component
  - [ ] Test form fields render
  - [ ] Test validation
  - [ ] Test submit creates session
  - [ ] Test edit mode populates fields
- [ ] Task: Implement CalibrationSessionForm.vue component
  - [ ] Create form with name, description, review cycle
  - [ ] Add review selection (multi-select or filter)
  - [ ] Add participant selection
  - [ ] Handle create and edit modes
- [ ] Task: Write tests for CalibrationSessionDetail component
  - [ ] Test displays session info
  - [ ] Test shows status workflow actions
  - [ ] Test start/complete buttons work
- [ ] Task: Implement CalibrationSessionDetail.vue component
  - [ ] Display session metadata
  - [ ] Show status with available actions
  - [ ] Implement start and complete actions
- [ ] Task: Add i18n translations for calibration UI (EN/NL/ES)
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Calibration Frontend - Session Management' (Protocol in workflow.md)

## Phase 7: Calibration Frontend - Grid View & Score Adjustment

- [ ] Task: Write tests for CalibrationNineGrid component
  - [ ] Test displays all session employees on grid
  - [ ] Test hover shows employee details
  - [ ] Test click opens detail panel
  - [ ] Test handles many employees gracefully
- [ ] Task: Implement CalibrationNineGrid.vue component
  - [ ] Extend TeamNineGrid for calibration context
  - [ ] Add employee detail panel on click
  - [ ] Handle dense cell populations
- [ ] Task: Write tests for ScoreAdjustmentPanel component
  - [ ] Test displays current scores
  - [ ] Test allows score editing
  - [ ] Test requires rationale
  - [ ] Test submits adjustment
- [ ] Task: Implement ScoreAdjustmentPanel.vue component
  - [ ] Show current WHAT and HOW scores
  - [ ] Add score edit controls
  - [ ] Add rationale textarea (required)
  - [ ] Submit adjustment to API
  - [ ] Show success/error feedback
- [ ] Task: Write tests for CalibrationNotesPanel component
  - [ ] Test displays existing notes
  - [ ] Test add new note
  - [ ] Test session vs review level notes
- [ ] Task: Implement CalibrationNotesPanel.vue component
  - [ ] List existing notes with author and timestamp
  - [ ] Add new note form
  - [ ] Support session and review level
- [ ] Task: Integrate components into CalibrationSessionView
  - [ ] Combine grid, adjustment panel, and notes
  - [ ] Handle component communication
  - [ ] Refresh grid after score adjustment
- [ ] Task: Add i18n translations for calibration grid UI (EN/NL/ES)
- [ ] Task: Conductor - User Manual Verification 'Phase 7: Calibration Frontend - Grid View & Score Adjustment' (Protocol in workflow.md)
