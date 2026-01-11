# Plan: Goal Setting IDE/TOV Enhancement

## Phase 1: Database Schema Updates [checkpoint: 2818148]

- [x] Task: Add review header fields to database `57980a4`
  - [x] Write migration SQL for job_title, tov_level columns
  - [x] Write migration SQL for goal_setting_completed_at, mid_year_completed_at, end_year_completed_at columns
  - [x] Verify manager_id exists on reviews table (add if missing)
  - [x] Run migration and verify schema

- [x] Task: Update review repository for new fields `b66214d`
  - [x] Write tests for get_review returning new fields
  - [x] Write tests for update_review with job_title, tov_level
  - [x] Write tests for manager reassignment
  - [x] Implement repository updates

- [x] Task: Conductor - User Manual Verification 'Database Schema Updates' (Protocol in workflow.md) `2818148`

## Phase 2: Backend API - Review Header [checkpoint: ]

- [x] Task: Update GET /api/v1/reviews/{id} response `86a84a3`
  - [x] Write tests for response including all header fields
  - [x] Write tests for employee_name and manager_name resolution
  - [x] Write tests for stage completion timestamps
  - [x] Update schema and endpoint implementation

- [x] Task: Update PUT /api/v1/reviews/{id} for job_title and tov_level `b9ced05`
  - [x] Write tests for updating job_title in DRAFT status
  - [x] Write tests for updating tov_level in DRAFT status
  - [x] Write tests for rejection when not in DRAFT status
  - [x] Implement endpoint updates with validation

- [x] Task: Update goal submission validation `cf5b6c1`
  - [x] Write tests for submission rejection when job_title missing
  - [x] Write tests for submission rejection when tov_level missing
  - [x] Write tests for goal_setting_completed_at timestamp set on approval
  - [x] Implement validation and timestamp updates

- [x] Task: Implement review creation with pre-population `a4885f2`
  - [x] Write tests for pre-populating job_title from previous year
  - [x] Write tests for pre-populating tov_level from previous year
  - [x] Write tests for setting manager_id from employee's current manager
  - [x] Implement review creation logic

- [ ] Task: Conductor - User Manual Verification 'Backend API - Review Header' (Protocol in workflow.md)

## Phase 3: Backend API - Manager Reassignment [checkpoint: ]

- [ ] Task: Implement PUT /api/v1/reviews/{id}/manager endpoint
  - [ ] Write tests for HR role authorization
  - [ ] Write tests for successful manager reassignment
  - [ ] Write tests for invalid manager_id rejection
  - [ ] Write tests for audit log creation with old/new manager
  - [ ] Implement endpoint with RBAC

- [ ] Task: Add manager reassignment audit logging
  - [ ] Write tests for audit log entry format
  - [ ] Write tests for optional reason field capture
  - [ ] Implement audit log service integration

- [ ] Task: Conductor - User Manual Verification 'Backend API - Manager Reassignment' (Protocol in workflow.md)

## Phase 4: Frontend - Review Header Component [checkpoint: ]

- [ ] Task: Create ReviewHeader component
  - [ ] Write tests for displaying employee name, manager name, review year
  - [ ] Write tests for displaying stage dates (completed or "Pending")
  - [ ] Write tests for job title input (editable in DRAFT)
  - [ ] Write tests for TOV level dropdown (editable in DRAFT)
  - [ ] Write tests for read-only mode after submission
  - [ ] Implement ReviewHeader.vue with Card styling

- [ ] Task: Integrate auto-save for header fields
  - [ ] Write tests for job_title auto-save on change
  - [ ] Write tests for tov_level auto-save on change
  - [ ] Implement auto-save using existing useAutoSave composable
  - [ ] Connect SaveIndicator for feedback

- [ ] Task: Add i18n translations for header labels
  - [ ] Add English translations
  - [ ] Add Dutch translations
  - [ ] Add Spanish translations

- [ ] Task: Integrate ReviewHeader into GoalSettingView
  - [ ] Write tests for header visibility at top of page
  - [ ] Write tests for data flow from API to header
  - [ ] Update GoalSettingView layout

- [ ] Task: Conductor - User Manual Verification 'Frontend - Review Header Component' (Protocol in workflow.md)

## Phase 5: Frontend - Competency Preview [checkpoint: ]

- [ ] Task: Create CompetencyPreview component
  - [ ] Write tests for displaying 6 competencies grouped by category
  - [ ] Write tests for competency name and description display
  - [ ] Write tests for empty state when no TOV level selected
  - [ ] Write tests for dynamic update on TOV level change
  - [ ] Implement CompetencyPreview.vue

- [ ] Task: Create useCompetencyPreview composable
  - [ ] Write tests for fetching competencies by TOV level
  - [ ] Write tests for caching to avoid redundant API calls
  - [ ] Write tests for loading state management
  - [ ] Implement composable with API integration

- [ ] Task: Add i18n translations for preview section
  - [ ] Add English translations (header, empty state, category names)
  - [ ] Add Dutch translations
  - [ ] Add Spanish translations

- [ ] Task: Integrate CompetencyPreview into GoalSettingView
  - [ ] Write tests for preview appearing below goals list
  - [ ] Write tests for preview updating when header TOV changes
  - [ ] Update GoalSettingView layout

- [ ] Task: Conductor - User Manual Verification 'Frontend - Competency Preview' (Protocol in workflow.md)

## Phase 6: Frontend - HR Manager Reassignment [checkpoint: ]

- [ ] Task: Create ManagerReassignModal component
  - [ ] Write tests for modal rendering with manager dropdown
  - [ ] Write tests for optional reason field
  - [ ] Write tests for submit and cancel actions
  - [ ] Write tests for loading and error states
  - [ ] Implement ManagerReassignModal.vue

- [ ] Task: Add reassign button to ReviewHeader for HR role
  - [ ] Write tests for button visibility only for HR role
  - [ ] Write tests for modal opening on click
  - [ ] Write tests for header update after successful reassignment
  - [ ] Implement conditional button and modal integration

- [ ] Task: Create manager reassignment API client
  - [ ] Write tests for reassignManager function
  - [ ] Write tests for error handling
  - [ ] Implement in frontend/src/api/reviews.ts

- [ ] Task: Add i18n translations for reassignment UI
  - [ ] Add English translations
  - [ ] Add Dutch translations
  - [ ] Add Spanish translations

- [ ] Task: Conductor - User Manual Verification 'Frontend - HR Manager Reassignment' (Protocol in workflow.md)

## Phase 7: Validation & Submission Updates [checkpoint: ]

- [ ] Task: Update goal submission UI validation
  - [ ] Write tests for submit button disabled when job_title empty
  - [ ] Write tests for submit button disabled when tov_level empty
  - [ ] Write tests for validation error messages display
  - [ ] Update GoalSettingView submission logic

- [ ] Task: Update stage completion timestamp handling
  - [ ] Write tests for goal_setting_completed_at display after approval
  - [ ] Verify mid_year_completed_at updates (in scoring flow)
  - [ ] Verify end_year_completed_at updates (in scoring flow)

- [ ] Task: Conductor - User Manual Verification 'Validation & Submission Updates' (Protocol in workflow.md)

## Phase 8: Integration Testing & Polish [checkpoint: ]

- [ ] Task: End-to-end goal setting flow testing
  - [ ] Test complete flow with header fields
  - [ ] Test job_title and tov_level pre-population from previous year
  - [ ] Test competency preview updates
  - [ ] Test submission validation

- [ ] Task: End-to-end manager reassignment testing
  - [ ] Test HR reassignment flow
  - [ ] Verify audit log entries
  - [ ] Test review access after reassignment

- [ ] Task: Responsive design verification
  - [ ] Test header layout on desktop
  - [ ] Test header stacking on tablet/mobile
  - [ ] Test competency preview on mobile

- [ ] Task: Conductor - User Manual Verification 'Integration Testing & Polish' (Protocol in workflow.md)
