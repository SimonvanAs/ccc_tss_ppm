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

- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) `5f1b4fd`

## Phase 2: Frontend - Team Dashboard

- [ ] Task: Create team API client module
  - [ ] Write tests for `fetchTeamMembers` function
  - [ ] Implement `frontend/src/api/team.ts`

- [ ] Task: Create TeamDashboard view
  - [ ] Write component tests for team list rendering
  - [ ] Implement `frontend/src/views/TeamDashboardView.vue`
  - [ ] Add route `/team` to router

- [ ] Task: Create TeamMemberCard component
  - [ ] Write tests for status badge rendering (Not Started/In Progress/Complete)
  - [ ] Write tests for click navigation
  - [ ] Implement `frontend/src/components/dashboard/TeamMemberCard.vue`

- [ ] Task: Add team dashboard to navigation
  - [ ] Update App.vue or navigation component for manager role
  - [ ] Write tests for role-based navigation visibility

- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

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

- [ ] Task: Conductor - User Manual Verification 'Phase 6' (Protocol in workflow.md)
