# Goal Setting IDE/TOV Enhancement

## Overview

This track enhances the Employee Goal Setting workflow to include a comprehensive review header section with employee details, manager assignment, review dates, job title, and TOV level selection. Manager, job title, and TOV level are stored per-review as they can change annually (or mid-year for managers). HR can reassign reviews to a different manager when needed. The TOV level determines which 6 competencies will be used for HOW-axis scoring. A competency preview section shows the applicable competencies before submission.

## Functional Requirements

### FR-1: Review Header Section

- **FR-1.1**: Review header appears at the top of the Goal Setting page
- **FR-1.2**: Header displays employee information:
  - Employee name (from user profile, read-only)
  - Manager name (from review assignment, read-only for employee/manager)
  - Review year (e.g., "2026", read-only)
- **FR-1.3**: Header displays review stage dates:
  - Goal Setting date (when goals were approved, or "Pending")
  - Mid-Year Review date (when mid-year was signed, or "Pending")
  - End-Year Review date (when end-year was signed, or "Pending")
- **FR-1.4**: Header includes editable job title field:
  - Text input for current job title
  - Pre-populated from previous year's review if available
  - Required before goal submission
- **FR-1.5**: Header includes TOV level dropdown:
  - Options: Level A, Level B, Level C, Level D
  - Pre-populated from previous year's review if available
  - Required before goal submission
- **FR-1.6**: Job title and TOV level are editable while review is in DRAFT status
- **FR-1.7**: Job title and TOV level become read-only after goal submission
  - Display as text instead of inputs
  - Tooltip explains why they cannot be changed

### FR-2: Manager Assignment (HR Only)

- **FR-2.1**: Manager is stored on the review record (not derived from employee profile)
- **FR-2.2**: Manager assigned at review creation (typically from employee's current manager)
- **FR-2.3**: HR can reassign review to a different manager at any time
  - Via HR dashboard or review management screen
  - Dropdown shows eligible managers within OpCo
- **FR-2.4**: Manager reassignment creates audit log entry
  - Records: old_manager_id, new_manager_id, changed_by, timestamp, reason (optional)
- **FR-2.5**: Employee and Manager roles see manager as read-only in review header
- **FR-2.6**: Notifications sent when manager is reassigned (future track)

### FR-3: Competency Preview Section

- **FR-3.1**: Competency preview section appears below the WHAT goals list
- **FR-3.2**: Section displays the 6 competencies for the selected TOV level
  - Grouped by category (Dedicated, Entrepreneurial, Innovative)
  - Shows competency name and brief description
- **FR-3.3**: Preview updates dynamically when TOV level changes
- **FR-3.4**: Empty state shown when no TOV level selected
  - Message: "Select a TOV level above to see which competencies will apply"
- **FR-3.5**: Section header: "HOW-axis Competencies (Preview)"
  - Subheader indicating these will be scored during Mid-Year/End-Year review

### FR-4: Backend API Updates

- **FR-4.1**: Add/update fields on review record:
  - `manager_id` - UUID, required (already exists, ensure it's on review not derived)
  - `job_title` - VARCHAR(255), nullable
  - `tov_level` - ENUM('A', 'B', 'C', 'D'), nullable
  - `goal_setting_completed_at` - TIMESTAMP, nullable
  - `mid_year_completed_at` - TIMESTAMP, nullable
  - `end_year_completed_at` - TIMESTAMP, nullable
- **FR-4.2**: `PUT /api/v1/reviews/{id}` accepts job_title and tov_level updates
  - Only allowed when status is DRAFT
  - Returns 400 if review is not in DRAFT status
- **FR-4.3**: `PUT /api/v1/reviews/{id}/manager` (HR only) reassigns manager
  - Request: `{ "manager_id": "uuid", "reason": "optional string" }`
  - Creates audit log entry
  - Returns updated review
- **FR-4.4**: `GET /api/v1/reviews/{id}` returns all header fields:
  - employee_id, employee_name
  - manager_id, manager_name
  - review_year
  - job_title, tov_level
  - goal_setting_completed_at, mid_year_completed_at, end_year_completed_at
- **FR-4.5**: Goal submission validates both job_title and tov_level are set
  - Returns 400 with clear error message listing missing fields
- **FR-4.6**: Stage completion updates appropriate timestamp:
  - Goal approval → goal_setting_completed_at
  - Mid-year sign-off → mid_year_completed_at
  - End-year sign-off → end_year_completed_at
- **FR-4.7**: Review creation pre-populates from previous year's review (if exists):
  - job_title, tov_level
  - manager_id from employee's current manager assignment

### FR-5: Database Schema

- **FR-5.1**: Ensure/add columns to reviews table:
  - `manager_id` UUID NOT NULL REFERENCES users(id)
  - `job_title` VARCHAR(255) NULL
  - `tov_level` VARCHAR(1) NULL CHECK (tov_level IN ('A', 'B', 'C', 'D'))
  - `goal_setting_completed_at` TIMESTAMP NULL
  - `mid_year_completed_at` TIMESTAMP NULL
  - `end_year_completed_at` TIMESTAMP NULL
- **FR-5.2**: Migration preserves existing review data (new fields nullable)

### FR-6: UI Layout

- **FR-6.1**: Review header layout (top of page):
  ```
  ┌─────────────────────────────────────────────────────────────┐
  │  Employee: John Doe              Manager: Jane Smith        │
  │  Review Year: 2026                                          │
  ├─────────────────────────────────────────────────────────────┤
  │  Job Title: [Senior Developer    ]  TOV Level: [Level B ▼]  │
  ├─────────────────────────────────────────────────────────────┤
  │  Goal Setting: 2026-02-15 │ Mid-Year: Pending │ End-Year: Pending │
  └─────────────────────────────────────────────────────────────┘
  ```
- **FR-6.2**: Use Card component for header section
- **FR-6.3**: Apply brand styling (Navy headers, Magenta accents)
- **FR-6.4**: HR view shows "Reassign Manager" button next to manager name

## Non-Functional Requirements

- **NFR-1**: Competency preview loads within 500ms of TOV selection
- **NFR-2**: Job title and TOV level persist via auto-save (same as goals)
- **NFR-3**: Multi-language support for all labels and competency descriptions (EN/NL/ES)
- **NFR-4**: Header is responsive (stacks on mobile)
- **NFR-5**: Manager reassignment logged in audit_logs table

## Acceptance Criteria

1. Review header visible at top of Goal Setting page
2. Header shows employee name, manager name, review year
3. Header shows three stage dates (Goal Setting, Mid-Year, End-Year)
4. Job title input editable during DRAFT, pre-populated from previous year
5. TOV level dropdown editable during DRAFT, pre-populated from previous year
6. Both fields become read-only after goal submission
7. Goal submission fails with error if job title or TOV level missing
8. Competency preview section shows below goals list
9. Preview displays 6 competencies grouped by category for selected TOV
10. Preview updates dynamically when TOV level changes
11. HR can reassign manager via dedicated endpoint/UI
12. Manager reassignment creates audit log entry
13. Stage completion dates update when each stage is signed off
14. Existing reviews without new fields continue to work

## Out of Scope

- Changing job title or TOV level after goal submission (requires separate HR override feature)
- Custom competency selection per employee
- Manager reassignment notifications (separate track)
- Bulk manager reassignment for team transfers
- Historical manager tracking per stage (uses single manager per review)
