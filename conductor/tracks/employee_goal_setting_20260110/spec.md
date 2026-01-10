# Specification: Employee Goal Setting Workflow

## Overview

This track implements the core goal management functionality for the Employee Goal Setting stage of the review workflow. Employees will be able to create, edit, reorder, and submit their goals with proper weight validation.

## User Story

**As an** Employee
**I want to** manage my performance goals for the upcoming review period
**So that** my manager can review and approve them before the review cycle begins

## Acceptance Criteria

### Goal Management
- [ ] Employee can view their current goals for an active review
- [ ] Employee can add new goals (maximum 9 goals per review)
- [ ] Employee can edit goal title (required, max 500 characters)
- [ ] Employee can edit goal description (optional, free text with voice input)
- [ ] Employee can set goal type: Standard, KAR (Key Achievement Required), or SCF (Success Critical Factor)
- [ ] Employee can set goal weight (5-100%, increments of 5%)
- [ ] Employee can delete goals (with confirmation)
- [ ] Employee can reorder goals via drag-and-drop

### Weight Validation
- [ ] Total weight of all goals must equal exactly 100%
- [ ] Display running total of weights as goals are edited
- [ ] Show clear error state when weights don't total 100%
- [ ] Block submission until weights are valid

### Auto-Save
- [ ] Changes auto-save after 2-3 seconds of inactivity
- [ ] Visual indicator shows save status (saving, saved, error)
- [ ] Unsaved changes warning if navigating away

### Submission
- [ ] Employee can submit goals for manager approval when weights total 100%
- [ ] Submission changes review status to PENDING_MANAGER_SIGNATURE
- [ ] Manager receives notification of pending goal approval

### Voice Input
- [ ] Voice input available for goal description field
- [ ] Hold-to-dictate interaction
- [ ] Appends to existing text

## Technical Requirements

### Backend API Endpoints
```
GET    /api/v1/reviews/:id/goals     # List goals for a review
POST   /api/v1/reviews/:id/goals     # Create new goal
PUT    /api/v1/goals/:id             # Update goal
DELETE /api/v1/goals/:id             # Delete goal
PUT    /api/v1/reviews/:id/goals/order  # Reorder goals
POST   /api/v1/reviews/:id/submit    # Submit goals for approval
```

### Database Tables
- `goals` table (already defined in schema)
- `reviews` table (status transitions)

### Frontend Components
- `GoalList.vue` - Container for goal items with drag-drop
- `GoalItem.vue` - Individual goal card with inline editing
- `GoalForm.vue` - Modal/panel for detailed goal editing
- `WeightIndicator.vue` - Visual weight total display
- `VoiceInput.vue` - Hold-to-dictate component (reusable)

### Validation Rules
- Goal title: required, 1-500 characters
- Goal weight: 5-100, must be multiple of 5
- Total weights: must equal 100
- Maximum goals: 9 per review
- Goal type: enum ['STANDARD', 'KAR', 'SCF']

## Out of Scope
- Manager approval workflow (separate track)
- Goal scoring (happens in Mid-Year/End-Year stages)
- Goal change requests (post-approval modifications)
- Competency (HOW-axis) management
- PDF report generation

## Dependencies
- Keycloak authentication must be functional
- Database schema must be deployed
- User must have an active review in GOAL_SETTING stage

## UI/UX Notes
- Follow product guidelines (friendly tone, helpful error messages)
- Desktop-first but mobile-functional
- Clean, minimal design with clear primary action
- Brand colors: Magenta (#CC0E70) for primary actions
