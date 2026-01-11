# Plan: Manager Goal Scoring

## Phase 1: Backend API - Team & Scores Endpoints [checkpoint: 5f1b4fd]

- [x] Task: Create team repository with raw SQL queries `aa32289`
  - [x] Write tests for `get_team_members_by_manager_id` query
  - [x] Implement `TeamRepository` class in `backend/src/repositories/team.py`
  - [x] Write tests for team member status calculation (Not Started/In Progress/Complete)
  - [x] Implement status logic in repository

- [x] Task: Create scores repository with raw SQL queries `ed6d33f`
  - [x] Write tests for `get_scores_by_review_id` query
  - [x] Write tests for `upsert_scores` query (insert or update)
  - [x] Implement `ScoresRepository` class in `backend/src/repositories/scores.py`

- [x] Task: Create GET /api/v1/manager/team endpoint `b2176dc`
  - [x] Write API tests for endpoint with auth (manager role required)
  - [x] Implement router in `backend/src/routers/manager.py`
  - [x] Add Pydantic schemas for team member response

- [x] Task: Create GET /api/v1/reviews/{id}/scores endpoint `cac9fc8`
  - [x] Write API tests for endpoint with auth and authorization
  - [x] Implement router handler in `backend/src/routers/reviews.py`
  - [x] Add Pydantic schemas for scores response

- [x] Task: Create PUT /api/v1/reviews/{id}/scores endpoint `cac9fc8`
  - [x] Write API tests for score creation/update
  - [x] Write API tests for partial score saves
  - [x] Implement router handler with upsert logic
  - [x] Add Pydantic schemas for scores request

- [x] Task: Create GET /api/v1/competencies endpoint `6743b95`
  - [x] Write API tests for competencies by TOV level
  - [x] Implement router in `backend/src/routers/competencies.py`
  - [x] Add Pydantic schemas for competency response

- [ ] Task: Create POST /api/v1/reviews/{id}/submit-scores endpoint
  - [ ] Write API tests for status transition (DRAFT → PENDING_EMPLOYEE_SIGNATURE)
  - [ ] Write API tests for validation (all scores required before submit)
  - [ ] Write API tests for authorization (only manager of review can submit)
  - [ ] Write API tests for idempotency (prevent re-submission)
  - [ ] Implement router handler in `backend/src/routers/reviews.py`
  - [ ] Add audit log entry for status transition

- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) `5f1b4fd`

## Phase 2: Frontend - Team Dashboard [checkpoint: 06595cb]

- [x] Task: Create team API client module `d25f75a`
  - [x] Write tests for `fetchTeamMembers` function
  - [x] Implement `frontend/src/api/team.ts`

- [x] Task: Create TeamDashboard view `c88c560`
  - [x] Write component tests for team list rendering
  - [x] Implement `frontend/src/views/TeamDashboardView.vue`
  - [x] Add route `/team` to router

- [x] Task: Create TeamMemberCard component `12cb594`
  - [x] Write tests for status badge rendering (Not Started/In Progress/Complete)
  - [x] Write tests for click navigation
  - [x] Implement `frontend/src/components/dashboard/TeamMemberCard.vue`

- [x] Task: Add team dashboard to navigation `8412901`
  - [x] Update App.vue or navigation component for manager role
  - [x] Write tests for role-based navigation visibility

- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) `06595cb`

## Phase 3: Frontend - Score Card Component & VETO Logic [checkpoint: 7523c86]

- [x] Task: Create scoring service with VETO calculations
  - [x] Write tests for weighted WHAT score calculation
  - [x] Write tests for HOW score calculation
  - [x] Write tests for SCF VETO rule (SCF=1 → WHAT=1.00)
  - [x] Write tests for KAR VETO rule with compensation logic
  - [x] Write tests for competency VETO rule (any=1 → HOW=1.00)
  - [x] Implement `frontend/src/services/scoring.ts`

- [x] Task: Create ScoreCard component `a95d919`
  - [x] Write tests for three-card display (1, 2, 3)
  - [x] Write tests for selection state and visual feedback
  - [x] Write tests for click handler emitting score
  - [x] Implement `frontend/src/components/review/ScoreCard.vue`

- [x] Task: Create VetoWarning component `0567343`
  - [x] Write tests for SCF VETO warning display
  - [x] Write tests for KAR VETO warning with compensation indicator
  - [x] Write tests for competency VETO warning display
  - [x] Implement `frontend/src/components/review/VetoWarning.vue`

- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md) `7523c86`

## Phase 4: Frontend - 9-Grid Visualization [checkpoint: 51587f1]

- [x] Task: Create NineGrid component `579a419`
  - [x] Write tests for 3x3 grid rendering
  - [x] Write tests for position calculation from WHAT/HOW scores
  - [x] Write tests for cell color coding (Red/Orange/Green/Dark Green)
  - [x] Write tests for real-time position updates
  - [x] Implement `frontend/src/components/review/NineGrid.vue`

- [x] Task: Create ScoreSummary component `bbc0563`
  - [x] Write tests for WHAT score display
  - [x] Write tests for HOW score display
  - [x] Write tests for VETO indicator integration
  - [x] Implement `frontend/src/components/review/ScoreSummary.vue`

- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md) `51587f1`

## Phase 5: Frontend - Scoring View with Auto-Save

- [x] Task: Create scores API client module `9ea0895`
  - [x] Write tests for `fetchScores` function
  - [x] Write tests for `saveScores` function with debouncing
  - [x] Implement `frontend/src/api/scores.ts`

- [x] Task: Create useScoring composable `8b42a43`
  - [x] Write tests for score state management
  - [x] Write tests for auto-save with debounce (500ms)
  - [x] Write tests for save status tracking (Saving/Saved/Error)
  - [x] Write tests for loading existing scores
  - [x] Implement `frontend/src/composables/useScoring.ts`

- [x] Task: Create GoalScoringSection component `158bf73`
  - [x] Write tests for goal list with score cards
  - [x] Write tests for feedback text area per goal
  - [x] Write tests for voice input integration
  - [x] Implement `frontend/src/components/review/GoalScoringSection.vue`

- [x] Task: Create CompetencyScoringSection component `8b9a8c9`
  - [x] Write tests for competency list by category
  - [x] Write tests for score cards per competency
  - [x] Implement `frontend/src/components/review/CompetencyScoringSection.vue`

- [x] Task: Create ReviewScoringView page
  - [x] Write tests for full page integration
  - [x] Write tests for auto-save status indicator
  - [x] Write tests for 9-Grid sidebar integration
  - [x] Implement `frontend/src/views/ReviewScoringView.vue`
  - [x] Add route `/reviews/:id/score` to router

- [x] Task: Create SubmitScoresButton component
  - [x] Write tests for disabled state when scores incomplete
  - [x] Write tests for enabled state when all scores entered
  - [x] Write tests for confirmation dialog display
  - [x] Write tests for API call on confirmation
  - [x] Implement `frontend/src/components/review/SubmitScoresButton.vue`

- [x] Task: Create ConfirmationDialog component
  - [x] Write tests for dialog content and actions
  - [x] Write tests for cancel and confirm behavior
  - [x] Implement `frontend/src/components/common/ConfirmationDialog.vue`

- [x] Task: Implement read-only scoring view mode
  - [x] Write tests for read-only state detection based on review status
  - [x] Write tests for disabled score cards in read-only mode
  - [x] Write tests for hidden submit button in read-only mode
  - [x] Update ReviewScoringView to support read-only mode

- [x] Task: Add submit-scores API client function
  - [x] Write tests for `submitScores` function
  - [x] Write tests for success redirect to team dashboard
  - [x] Write tests for error handling
  - [x] Implement in `frontend/src/api/scores.ts`

- [ ] Task: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)

## Phase 6: Internationalization & Polish

- [ ] Task: Add i18n translations for scoring UI
  - [ ] Add English translations to `frontend/src/i18n/en.json`
  - [ ] Add Dutch translations to `frontend/src/i18n/nl.json`
  - [ ] Add Spanish translations to `frontend/src/i18n/es.json`

- [ ] Task: Add responsive styles for tablet/mobile
  - [ ] Write visual tests for mobile layout
  - [ ] Implement responsive CSS for scoring components

- [ ] Task: End-to-end integration testing
  - [ ] Test complete scoring flow from team dashboard to 9-grid
  - [ ] Test auto-save persistence across page reloads
  - [ ] Test VETO warning display scenarios
  - [ ] Test submit scores flow with confirmation dialog
  - [ ] Test status transition and redirect to dashboard
  - [ ] Test read-only mode for submitted reviews

- [ ] Task: Conductor - User Manual Verification 'Phase 6' (Protocol in workflow.md)
