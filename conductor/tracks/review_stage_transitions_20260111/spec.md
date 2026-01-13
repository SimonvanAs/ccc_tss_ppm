# Track: Review Stage Transitions

## Priority: CRITICAL

## Summary
Implement the review stage transition system to enable the annual review cycle progression from GOAL_SETTING → MID_YEAR_REVIEW → END_YEAR_REVIEW.

## Problem Statement
Currently there is no endpoint to advance reviews between stages. This blocks the entire annual review cycle - reviews are stuck in GOAL_SETTING stage forever.

## Requirements
Based on `/requirements/Review-Workflow-States.md`:

1. **Stage Transition Endpoint**
   - POST `/api/v1/reviews/{review_id}/advance-stage`
   - Only HR or system can advance stages
   - Validates current stage is SIGNED before advancing
   - Resets status to DRAFT when entering new stage

2. **Stage Transition Rules**
   - GOAL_SETTING → MID_YEAR_REVIEW: After manager signs off on goals
   - MID_YEAR_REVIEW → END_YEAR_REVIEW: After mid-year review completion
   - END_YEAR_REVIEW → ARCHIVED: After final signatures and calibration

3. **Bulk Stage Advancement**
   - POST `/api/v1/admin/reviews/advance-stage`
   - HR can advance all reviews in an OpCo to next stage
   - Used for annual cycle milestones

4. **Stage-Specific UI Updates**
   - GoalSettingView: Only editable in GOAL_SETTING stage
   - ReviewScoringView: Different behavior per stage
   - Dashboard: Show current stage prominently

## Acceptance Criteria
- [ ] Single review stage advancement endpoint works
- [ ] Bulk stage advancement for OpCo works
- [ ] Stage transition validates SIGNED status
- [ ] Status resets to DRAFT on stage change
- [ ] UI reflects current stage correctly
- [ ] Audit log records stage transitions
- [ ] Tests cover all stage transitions

## Technical Notes
- Database already has `stage` column with enum
- `goal_setting_completed_at`, `mid_year_completed_at`, `end_year_completed_at` timestamps exist
- Need to clear signatures when advancing stage

## Dependencies
- None (core functionality)

## Estimated Effort
- Backend: 4 hours
- Frontend: 2 hours
- Testing: 2 hours
