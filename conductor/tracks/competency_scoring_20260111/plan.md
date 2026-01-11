# Plan: Competency Scoring

## Phase 1: Backend Scoring Service

- [x] Task: Write tests for HOW score calculation service `00ddce6`
  - [x] Test average calculation when all scores present
  - [x] Test VETO rule when any score equals 1
  - [x] Test grid position mapping (1.00-1.66→1, 1.67-2.33→2, 2.34-3.00→3)
  - [x] Test incomplete scores handling
- [x] Task: Implement scoring service (`backend/src/services/scoring.py`) `00ddce6`
  - [x] Create `calculate_how_score()` function
  - [x] Create `calculate_grid_position()` function
  - [x] Create `check_how_veto()` function
- [x] Task: Write tests for review score persistence `8dbab42`
  - [x] Test how_score update on competency score save
  - [x] Test how_veto_active flag update
  - [x] Test grid_position_how update
- [~] Task: Enhance scores repository to persist calculated HOW score
  - [ ] Update `bulk_upsert_competency_scores` to recalculate review scores
  - [ ] Add method to update review how_score fields
- [ ] Task: Conductor - User Manual Verification 'Backend Scoring Service' (Protocol in workflow.md)

## Phase 2: Frontend Scoring Composable

- [ ] Task: Write tests for useCompetencyScoring composable
  - [ ] Test HOW score calculation
  - [ ] Test VETO detection
  - [ ] Test grid position calculation
  - [ ] Test score completion tracking (X/6)
- [ ] Task: Implement useCompetencyScoring composable
  - [ ] Create reactive score state management
  - [ ] Implement `calculateHowScore()` function
  - [ ] Implement `checkVeto()` function
  - [ ] Implement `getGridPosition()` function
  - [ ] Implement `isComplete` computed property
- [ ] Task: Conductor - User Manual Verification 'Frontend Scoring Composable' (Protocol in workflow.md)

## Phase 3: Frontend Score Card Component

- [ ] Task: Write tests for CompetencyScoreCard component
  - [ ] Test renders three score buttons (1, 2, 3)
  - [ ] Test selected state visual feedback
  - [ ] Test click emits score-change event
  - [ ] Test disabled state
- [ ] Task: Implement CompetencyScoreCard.vue component
  - [ ] Create score button layout with labels
  - [ ] Add selected state styling (magenta highlight)
  - [ ] Emit score-change event on click
  - [ ] Support disabled prop
- [ ] Task: Add i18n translations for score labels (EN/NL/ES)
- [ ] Task: Conductor - User Manual Verification 'Frontend Score Card Component' (Protocol in workflow.md)

## Phase 4: Frontend Competency List Component

- [ ] Task: Write tests for CompetencyList component
  - [ ] Test fetches competencies for TOV level
  - [ ] Test renders 6 competencies grouped by category
  - [ ] Test score card integration
  - [ ] Test notes textarea with voice input
  - [ ] Test VETO highlight on score = 1
- [ ] Task: Implement CompetencyList.vue component
  - [ ] Fetch competencies from API on mount
  - [ ] Group competencies by category (Dedicated/Entrepreneurial/Innovative)
  - [ ] Display competency title, category badge, indicators
  - [ ] Integrate CompetencyScoreCard for each competency
  - [ ] Add notes textarea with VoiceInput component
  - [ ] Highlight row when score = 1 (VETO warning)
- [ ] Task: Add i18n translations for component text (EN/NL/ES)
- [ ] Task: Conductor - User Manual Verification 'Frontend Competency List Component' (Protocol in workflow.md)

## Phase 5: Frontend HOW Score Indicator

- [ ] Task: Write tests for HOWScoreIndicator component
  - [ ] Test displays calculated HOW score
  - [ ] Test VETO warning banner when active
  - [ ] Test grid position indicator
  - [ ] Test incomplete state display
- [ ] Task: Implement HOWScoreIndicator.vue component
  - [ ] Display HOW score value with 2 decimal places
  - [ ] Show VETO warning banner (magenta styling)
  - [ ] Display grid position (1, 2, or 3)
  - [ ] Show progress indicator (X/6 competencies scored)
- [ ] Task: Add i18n translations for indicator text (EN/NL/ES)
- [ ] Task: Conductor - User Manual Verification 'Frontend HOW Score Indicator' (Protocol in workflow.md)

## Phase 6: Integration and Auto-Save

- [ ] Task: Write integration tests for competency scoring flow
  - [ ] Test end-to-end score entry and save
  - [ ] Test auto-save triggers on score change
  - [ ] Test 9-Grid updates on HOW score change
- [ ] Task: Integrate CompetencyList into manager scoring view
  - [ ] Add CompetencyList to scoring page layout
  - [ ] Connect to useCompetencyScoring composable
  - [ ] Wire up auto-save with debounce (1 second)
  - [ ] Connect SaveIndicator component
- [ ] Task: Integrate HOW score with 9-Grid component
  - [ ] Emit HOW score changes to parent view
  - [ ] Update 9-Grid column position on score change
- [ ] Task: Conductor - User Manual Verification 'Integration and Auto-Save' (Protocol in workflow.md)
