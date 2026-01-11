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

## Phase 3: Frontend - Score Card Component & VETO Logic

- [ ] Task: Create scoring service with VETO calculations
  - [ ] Write tests for weighted WHAT score calculation
  - [ ] Write tests for HOW score calculation
  - [ ] Write tests for SCF VETO rule (SCF=1 → WHAT=1.00)
  - [ ] Write tests for KAR VETO rule with compensation logic
  - [ ] Write tests for competency VETO rule (any=1 → HOW=1.00)
  - [ ] Implement `frontend/src/services/scoring.ts`

- [ ] Task: Create ScoreCard component
  - [ ] Write tests for three-card display (1, 2, 3)
  - [ ] Write tests for selection state and visual feedback
  - [ ] Write tests for click handler emitting score
  - [ ] Implement `frontend/src/components/review/ScoreCard.vue`

- [ ] Task: Create VetoWarning component
  - [ ] Write tests for SCF VETO warning display
  - [ ] Write tests for KAR VETO warning with compensation indicator
  - [ ] Write tests for competency VETO warning display
  - [ ] Implement `frontend/src/components/review/VetoWarning.vue`

- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Frontend - 9-Grid Visualization

- [ ] Task: Create NineGrid component
  - [ ] Write tests for 3x3 grid rendering
  - [ ] Write tests for position calculation from WHAT/HOW scores
  - [ ] Write tests for cell color coding (Red/Orange/Green/Dark Green)
  - [ ] Write tests for real-time position updates
  - [ ] Implement `frontend/src/components/review/NineGrid.vue`

- [ ] Task: Create ScoreSummary component
  - [ ] Write tests for WHAT score display
  - [ ] Write tests for HOW score display
  - [ ] Write tests for VETO indicator integration
  - [ ] Implement `frontend/src/components/review/ScoreSummary.vue`

- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)

## Phase 5: Frontend - Scoring View with Auto-Save

- [ ] Task: Create scores API client module
  - [ ] Write tests for `fetchScores` function
  - [ ] Write tests for `saveScores` function with debouncing
  - [ ] Implement `frontend/src/api/scores.ts`

- [ ] Task: Create useScoring composable
  - [ ] Write tests for score state management
  - [ ] Write tests for auto-save with debounce (500ms)
  - [ ] Write tests for save status tracking (Saving/Saved/Error)
  - [ ] Write tests for loading existing scores
  - [ ] Implement `frontend/src/composables/useScoring.ts`

- [ ] Task: Create GoalScoringSection component
  - [ ] Write tests for goal list with score cards
  - [ ] Write tests for feedback text area per goal
  - [ ] Write tests for voice input integration
  - [ ] Implement `frontend/src/components/review/GoalScoringSection.vue`

- [ ] Task: Create CompetencyScoringSection component
  - [ ] Write tests for competency list by category
  - [ ] Write tests for score cards per competency
  - [ ] Implement `frontend/src/components/review/CompetencyScoringSection.vue`

- [ ] Task: Create ReviewScoringView page
  - [ ] Write tests for full page integration
  - [ ] Write tests for auto-save status indicator
  - [ ] Write tests for 9-Grid sidebar integration
  - [ ] Implement `frontend/src/views/ReviewScoringView.vue`
  - [ ] Add route `/reviews/:id/score` to router

- [ ] Task: Create SubmitScoresButton component
  - [ ] Write tests for disabled state when scores incomplete
  - [ ] Write tests for enabled state when all scores entered
  - [ ] Write tests for confirmation dialog display
  - [ ] Write tests for API call on confirmation
  - [ ] Implement `frontend/src/components/review/SubmitScoresButton.vue`

- [ ] Task: Create ConfirmationDialog component
  - [ ] Write tests for dialog content and actions
  - [ ] Write tests for cancel and confirm behavior
  - [ ] Implement `frontend/src/components/common/ConfirmationDialog.vue`

- [ ] Task: Implement read-only scoring view mode
  - [ ] Write tests for read-only state detection based on review status
  - [ ] Write tests for disabled score cards in read-only mode
  - [ ] Write tests for hidden submit button in read-only mode
  - [ ] Update ReviewScoringView to support read-only mode

- [ ] Task: Add submit-scores API client function
  - [ ] Write tests for `submitScores` function
  - [ ] Write tests for success redirect to team dashboard
  - [ ] Write tests for error handling
  - [ ] Implement in `frontend/src/api/scores.ts`

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
