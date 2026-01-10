# Implementation Plan: Employee Goal Setting Workflow

## Track Overview
- **Track ID:** employee_goal_setting_20260110
- **Description:** Build the Employee Goal Setting workflow with goal CRUD, weight validation, and submission
- **Estimated Phases:** 4

---

## Phase 1: Backend Goal API Foundation

### Objective
Create the core backend API endpoints for goal management with proper authentication and validation.

### Tasks

- [x] Task: Set up backend project structure (36f07f9)
  - Create routers/, repositories/, services/, schemas/ directories under backend/src/
  - Set up database connection pool with asyncpg
  - Configure Keycloak JWT validation middleware

- [ ] Task: Write tests for Goal schema and validation
  - Create tests/test_schemas.py
  - Test GoalCreate, GoalUpdate, GoalResponse schemas
  - Test weight validation (5-100, multiples of 5)
  - Test goal type enum validation

- [ ] Task: Implement Goal Pydantic schemas
  - Create schemas/goal.py with GoalCreate, GoalUpdate, GoalResponse
  - Implement validation for weight constraints
  - Implement goal type enum

- [ ] Task: Write tests for Goal repository
  - Create tests/test_repositories.py
  - Test CRUD operations with mock database
  - Test weight total calculation query
  - Test goal ordering

- [ ] Task: Implement Goal repository
  - Create repositories/goals.py
  - Implement get_goals_by_review(), create_goal(), update_goal(), delete_goal()
  - Implement reorder_goals(), get_weight_total()
  - Use raw SQL with asyncpg

- [ ] Task: Write tests for Goal API endpoints
  - Create tests/test_api_goals.py
  - Test GET /reviews/:id/goals
  - Test POST /reviews/:id/goals
  - Test PUT /goals/:id
  - Test DELETE /goals/:id
  - Test PUT /reviews/:id/goals/order
  - Test authentication requirements
  - Test authorization (employee can only access own review)

- [ ] Task: Implement Goal API router
  - Create routers/goals.py
  - Implement all CRUD endpoints
  - Add authentication dependency
  - Add authorization checks (employee owns review)
  - Return proper HTTP status codes and error messages

- [ ] Task: Write tests for Review submission endpoint
  - Add tests to tests/test_api_reviews.py
  - Test POST /reviews/:id/submit
  - Test weight validation (must total 100%)
  - Test status transition to PENDING_MANAGER_SIGNATURE

- [ ] Task: Implement Review submission endpoint
  - Create/update routers/reviews.py
  - Implement submit endpoint with weight validation
  - Update review status on successful submission

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Backend Goal API Foundation' (Protocol in workflow.md)

---

## Phase 2: Frontend Goal List and Display

### Objective
Create the Vue components for displaying goals and the overall goal setting view.

### Tasks

- [ ] Task: Set up frontend project structure
  - Create api/, components/, composables/, views/, types/ directories under frontend/src/
  - Configure vue-router with protected routes
  - Set up Keycloak authentication service

- [ ] Task: Write tests for API client module
  - Create tests for api/goals.ts
  - Test fetchGoals(), createGoal(), updateGoal(), deleteGoal()
  - Test error handling
  - Mock fetch responses

- [ ] Task: Implement API client module
  - Create api/client.ts with auth interceptor
  - Create api/goals.ts with goal API functions
  - Handle token refresh and error responses

- [ ] Task: Write tests for Goal types
  - Create tests for types/goal.ts
  - Validate type definitions match API schemas

- [ ] Task: Implement Goal TypeScript types
  - Create types/goal.ts with Goal, GoalCreate, GoalUpdate interfaces
  - Create types/review.ts with Review interface
  - Export GoalType enum

- [ ] Task: Write tests for GoalItem component
  - Create tests for components/review/GoalItem.vue
  - Test rendering goal data
  - Test goal type badge display
  - Test weight display
  - Test edit/delete button visibility

- [ ] Task: Implement GoalItem component
  - Create components/review/GoalItem.vue
  - Display goal title, type badge, weight
  - Add edit and delete action buttons
  - Apply brand styling

- [ ] Task: Write tests for GoalList component
  - Create tests for components/review/GoalList.vue
  - Test rendering multiple goals
  - Test empty state
  - Test loading state

- [ ] Task: Implement GoalList component
  - Create components/review/GoalList.vue
  - Render list of GoalItem components
  - Show empty state when no goals
  - Show loading spinner while fetching

- [ ] Task: Write tests for WeightIndicator component
  - Create tests for components/review/WeightIndicator.vue
  - Test weight total display
  - Test valid state (100%)
  - Test invalid state (not 100%)
  - Test visual styling for states

- [ ] Task: Implement WeightIndicator component
  - Create components/review/WeightIndicator.vue
  - Display current total and target (100%)
  - Show success state when valid
  - Show error state when invalid
  - Use brand colors

- [ ] Task: Write tests for GoalSettingView
  - Create tests for views/GoalSettingView.vue
  - Test page layout
  - Test goal list integration
  - Test weight indicator integration

- [ ] Task: Implement GoalSettingView
  - Create views/GoalSettingView.vue
  - Integrate GoalList and WeightIndicator
  - Add page header and navigation
  - Add "Add Goal" button

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Frontend Goal List and Display' (Protocol in workflow.md)

---

## Phase 3: Goal Editing and Validation

### Objective
Implement goal creation, editing, deletion, and drag-drop reordering with proper validation.

### Tasks

- [ ] Task: Write tests for GoalForm component
  - Create tests for components/review/GoalForm.vue
  - Test form field rendering
  - Test validation messages
  - Test form submission
  - Test cancel behavior

- [ ] Task: Implement GoalForm component
  - Create components/review/GoalForm.vue
  - Add title input (required, max 500 chars)
  - Add description textarea
  - Add goal type dropdown (Standard, KAR, SCF)
  - Add weight slider/input (5-100, step 5)
  - Add save and cancel buttons
  - Display validation errors inline

- [ ] Task: Write tests for useGoals composable
  - Create tests for composables/useGoals.ts
  - Test goal CRUD operations
  - Test optimistic updates
  - Test error handling
  - Test weight calculation

- [ ] Task: Implement useGoals composable
  - Create composables/useGoals.ts
  - Manage goals state
  - Implement addGoal(), updateGoal(), deleteGoal()
  - Calculate total weight reactively
  - Handle API errors gracefully

- [ ] Task: Write tests for goal creation flow
  - Test opening GoalForm for new goal
  - Test validation on submit
  - Test successful creation
  - Test error handling

- [ ] Task: Implement goal creation flow
  - Add modal/panel for GoalForm
  - Wire up "Add Goal" button
  - Submit to API and refresh list
  - Show success/error feedback

- [ ] Task: Write tests for goal editing flow
  - Test opening GoalForm with existing goal data
  - Test field changes
  - Test save behavior
  - Test cancel without saving

- [ ] Task: Implement goal editing flow
  - Wire up edit button on GoalItem
  - Pre-populate GoalForm with goal data
  - Submit updates to API
  - Show success/error feedback

- [ ] Task: Write tests for goal deletion flow
  - Test delete confirmation dialog
  - Test successful deletion
  - Test cancel behavior
  - Test error handling

- [ ] Task: Implement goal deletion flow
  - Add confirmation dialog
  - Wire up delete button
  - Remove from list on success
  - Show success/error feedback

- [ ] Task: Write tests for drag-drop reordering
  - Test drag start/end events
  - Test order change
  - Test API call on drop
  - Test optimistic reorder

- [ ] Task: Implement drag-drop reordering
  - Add drag handles to GoalItem
  - Implement drag-drop logic in GoalList
  - Call reorder API on drop
  - Update local order optimistically

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Goal Editing and Validation' (Protocol in workflow.md)

---

## Phase 4: Auto-save, Voice Input, and Submission

### Objective
Complete the goal setting experience with auto-save, voice input for descriptions, and goal submission.

### Tasks

- [ ] Task: Write tests for useAutoSave composable
  - Create tests for composables/useAutoSave.ts
  - Test debounce timing (2-3 seconds)
  - Test save trigger on inactivity
  - Test dirty state tracking
  - Test save status states

- [ ] Task: Implement useAutoSave composable
  - Create composables/useAutoSave.ts
  - Track dirty fields
  - Debounce save calls (2500ms)
  - Expose save status (idle, saving, saved, error)

- [ ] Task: Write tests for SaveIndicator component
  - Create tests for components/common/SaveIndicator.vue
  - Test idle state
  - Test saving state (spinner)
  - Test saved state (checkmark)
  - Test error state

- [ ] Task: Implement SaveIndicator component
  - Create components/common/SaveIndicator.vue
  - Display appropriate icon/text per state
  - Use brand colors

- [ ] Task: Integrate auto-save into goal editing
  - Connect useAutoSave to GoalForm
  - Add SaveIndicator to UI
  - Test auto-save behavior end-to-end

- [ ] Task: Write tests for VoiceInput component
  - Create tests for components/common/VoiceInput.vue
  - Test idle state
  - Test recording state
  - Test processing state
  - Test error state
  - Test transcription callback

- [ ] Task: Implement VoiceInput component
  - Create components/common/VoiceInput.vue
  - Implement hold-to-dictate with MediaRecorder
  - Send audio to voice service API
  - Emit transcription result
  - Handle errors gracefully
  - Apply visual states (idle grey, recording magenta pulse, processing blue spinner, error red)

- [ ] Task: Integrate voice input into goal description
  - Add VoiceInput button to description field in GoalForm
  - Append transcription to existing text
  - Test integration end-to-end

- [ ] Task: Write tests for goal submission flow
  - Test submit button visibility (only when weights = 100%)
  - Test submit confirmation
  - Test successful submission
  - Test status change
  - Test error handling

- [ ] Task: Implement goal submission flow
  - Add submit button to GoalSettingView
  - Disable when weights != 100%
  - Call submit API endpoint
  - Show success message
  - Navigate to confirmation/dashboard

- [ ] Task: Write tests for unsaved changes warning
  - Test warning display when navigating with unsaved changes
  - Test confirm leave behavior
  - Test cancel leave behavior

- [ ] Task: Implement unsaved changes warning
  - Use beforeunload event
  - Use vue-router navigation guards
  - Show confirmation dialog

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Auto-save, Voice Input, and Submission' (Protocol in workflow.md)

---

## Completion Checklist

- [ ] All backend API endpoints implemented and tested
- [ ] All frontend components implemented and tested
- [ ] Goal CRUD functionality working end-to-end
- [ ] Weight validation enforced
- [ ] Auto-save functioning with visual feedback
- [ ] Voice input working for goal descriptions
- [ ] Goal submission workflow complete
- [ ] Code coverage >80% for new code
- [ ] All code follows style guides
- [ ] Manual testing completed on desktop and mobile
