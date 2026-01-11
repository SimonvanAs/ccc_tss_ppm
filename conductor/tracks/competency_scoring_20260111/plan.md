# Plan: Competency Scoring

## Phase 1: Backend Scoring Service [checkpoint: a067c6a]

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
- [x] Task: Enhance scores repository to persist calculated HOW score `3f9c75e`
  - [x] Update `bulk_upsert_competency_scores` to recalculate review scores
  - [x] Add method to update review how_score fields
- [x] Task: Conductor - User Manual Verification 'Backend Scoring Service' (Protocol in workflow.md) `a067c6a`

## Phase 2: Frontend Scoring Composable [checkpoint: 838fc68]

- [x] Task: Write tests for useCompetencyScoring composable `7ccdefa`
  - [x] Test HOW score calculation
  - [x] Test VETO detection
  - [x] Test grid position calculation
  - [x] Test score completion tracking (X/6)
- [x] Task: Implement useCompetencyScoring composable `7ccdefa`
  - [x] Create reactive score state management
  - [x] Implement `calculateHowScore()` function
  - [x] Implement `checkVeto()` function
  - [x] Implement `getGridPosition()` function
  - [x] Implement `isComplete` computed property
- [x] Task: Conductor - User Manual Verification 'Frontend Scoring Composable' (Protocol in workflow.md) `838fc68`

## Phase 3: Frontend Score Card Component [checkpoint: 11cd2d4]

- [x] Task: Write tests for CompetencyScoreCard component `4f8aaae`
  - [x] Test renders three score buttons (1, 2, 3)
  - [x] Test selected state visual feedback
  - [x] Test click emits score-change event
  - [x] Test disabled state
- [x] Task: Implement CompetencyScoreCard.vue component `4f8aaae`
  - [x] Create score button layout with labels
  - [x] Add selected state styling (magenta highlight)
  - [x] Emit score-change event on click
  - [x] Support disabled prop
- [x] Task: Add i18n translations for score labels (EN/NL/ES) `4f8aaae`
- [x] Task: Conductor - User Manual Verification 'Frontend Score Card Component' (Protocol in workflow.md) `11cd2d4`

## Phase 4: Frontend Competency List Component [checkpoint: 1bdd5eb]

- [x] Task: Write tests for CompetencyList component `1078aca`
  - [x] Test fetches competencies for TOV level
  - [x] Test renders 6 competencies grouped by category
  - [x] Test score card integration
  - [x] Test notes textarea with voice input
  - [x] Test VETO highlight on score = 1
- [x] Task: Implement CompetencyList.vue component `1078aca`
  - [x] Fetch competencies from API on mount
  - [x] Group competencies by category (Dedicated/Entrepreneurial/Innovative)
  - [x] Display competency title, category badge, indicators
  - [x] Integrate CompetencyScoreCard for each competency
  - [x] Add notes textarea with VoiceInput component
  - [x] Highlight row when score = 1 (VETO warning)
- [x] Task: Add i18n translations for component text (EN/NL/ES) `4f8aaae`
- [x] Task: Conductor - User Manual Verification 'Frontend Competency List Component' (Protocol in workflow.md) `1bdd5eb`

## Phase 5: Frontend HOW Score Indicator [checkpoint: 074dec7]

- [x] Task: Write tests for HOWScoreIndicator component `76335e3`
  - [x] Test displays calculated HOW score
  - [x] Test VETO warning banner when active
  - [x] Test grid position indicator
  - [x] Test incomplete state display
- [x] Task: Implement HOWScoreIndicator.vue component `76335e3`
  - [x] Display HOW score value with 2 decimal places
  - [x] Show VETO warning banner (magenta styling)
  - [x] Display grid position (1, 2, or 3)
  - [x] Show progress indicator (X/6 competencies scored)
- [x] Task: Add i18n translations for indicator text (EN/NL/ES) `4f8aaae`
- [x] Task: Conductor - User Manual Verification 'Frontend HOW Score Indicator' (Protocol in workflow.md) `074dec7`

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
