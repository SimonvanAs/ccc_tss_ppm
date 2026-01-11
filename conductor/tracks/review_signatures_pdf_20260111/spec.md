# Review Signatures & PDF Generation

## Overview

This track implements the digital signature workflow for performance reviews and PDF-A report generation using WeasyPrint. It enables employees and managers to formally sign off on reviews at various stages, with rejection handling and feedback mechanisms. PDF reports can be previewed as drafts at any stage, with final reports generated once both parties have signed.

## Functional Requirements

### FR-1: Goal Setting Signature Flow

- **FR-1.1**: Employee can submit goals for manager approval (DRAFT → PENDING_MANAGER_SIGNATURE)
  - Guard: Goals must total exactly 100% weight
  - Action: Add to manager's task list
- **FR-1.2**: Manager can approve goals (PENDING_MANAGER_SIGNATURE → SIGNED)
  - Records approval timestamp in audit log
- **FR-1.3**: Manager can reject goals with feedback (PENDING_MANAGER_SIGNATURE → DRAFT)
  - Requires feedback note
  - Notifies employee
  - Creates audit log entry

### FR-2: Mid-Year/End-Year Signature Flow

- **FR-2.1**: Manager submits review for employee signature (DRAFT → PENDING_EMPLOYEE_SIGNATURE)
  - Guards: All goals scored, all competencies scored, summary comments provided
  - Action: Add to employee's task list
- **FR-2.2**: Employee signs review (PENDING_EMPLOYEE_SIGNATURE → EMPLOYEE_SIGNED)
  - Records signature timestamp
  - Creates audit log entry
  - Auto-transitions to PENDING_MANAGER_SIGNATURE
- **FR-2.3**: Employee rejects review with feedback (PENDING_EMPLOYEE_SIGNATURE → DRAFT)
  - Requires feedback note
  - Notifies manager
  - Creates audit log entry
- **FR-2.4**: Manager counter-signs review (PENDING_MANAGER_SIGNATURE → MANAGER_SIGNED)
  - Records signature timestamp
  - Creates audit log entry
  - Auto-transitions to SIGNED when both signatures present
- **FR-2.5**: Manager requests employee re-review (PENDING_MANAGER_SIGNATURE → PENDING_EMPLOYEE_SIGNATURE)
  - Clears employee signature
  - Requires feedback note
  - Notifies employee

### FR-3: Signature UI Components

- **FR-3.1**: Signature confirmation modal with:
  - Summary of what user is signing (stage, scores, key details)
  - Checkbox: "I have reviewed and agree with this assessment"
  - "Sign Review" button (disabled until checkbox checked)
  - "Cancel" button
- **FR-3.2**: Rejection modal with:
  - Required feedback text area
  - "Submit Feedback & Return" button
  - "Cancel" button
- **FR-3.3**: Signature status display showing:
  - Current status badge (e.g., "Awaiting Your Signature")
  - Signature timestamps when signed
  - Who signed and when

### FR-4: PDF Report Generation

- **FR-4.1**: Draft PDF preview available at any stage
  - Includes "DRAFT" watermark on all pages
  - Same content as final PDF
- **FR-4.2**: Final PDF generated for SIGNED reviews
  - No watermark
  - PDF-A format for archival compliance
- **FR-4.3**: PDF download button in review UI
  - Shows "Download Draft PDF" for non-SIGNED reviews
  - Shows "Download Final Report" for SIGNED reviews

### FR-5: PDF Report Content

- **FR-5.1**: Header section
  - OpCo logo (top-left)
  - Employee name and employee ID
  - Review year and stage
  - Manager name
- **FR-5.2**: Goals section (WHAT-axis)
  - Each goal with: title, type (Standard/KAR/SCF), weight, score
  - Goal comments/feedback
  - WHAT score with VETO indicator if applicable
- **FR-5.3**: Competencies section (HOW-axis)
  - Each competency with: name, category, score
  - Competency comments if any
  - HOW score with VETO indicator if applicable
- **FR-5.4**: 9-Grid visualization
  - 3×3 grid with employee position marked
  - Color coding: Red, Orange, Green, Dark Green
- **FR-5.5**: Comments section
  - Manager summary comments
  - Employee self-assessment comments
  - Any feedback notes from signature process
- **FR-5.6**: Signature section
  - Employee signature line with timestamp (or "Pending")
  - Manager signature line with timestamp (or "Pending")
- **FR-5.7**: Styling
  - Brand colors: Magenta (#CC0E70), Navy Blue (#004A91)
  - Tahoma font family
  - Professional corporate layout
  - Page breaks for readability

### FR-6: Backend API Endpoints

- **FR-6.1**: `POST /api/v1/reviews/{id}/submit` - Submit for signature
- **FR-6.2**: `POST /api/v1/reviews/{id}/sign` - Sign review
- **FR-6.3**: `POST /api/v1/reviews/{id}/reject` - Reject with feedback
- **FR-6.4**: `GET /api/v1/reviews/{id}/pdf` - Generate/download PDF
- **FR-6.5**: All endpoints enforce RBAC (employee can only sign own reviews, manager can only sign team reviews)

## Non-Functional Requirements

- **NFR-1**: PDF generation completes within 5 seconds
- **NFR-2**: All signature actions logged to audit_logs table
- **NFR-3**: PDF-A format compliance for long-term archival
- **NFR-4**: Signature timestamps stored in UTC
- **NFR-5**: Multi-language support for PDF content (EN/NL/ES)

## Acceptance Criteria

1. Employee can submit goals and manager can approve/reject with feedback
2. Manager can submit scored review for employee signature
3. Employee can sign or reject review with feedback
4. Manager can counter-sign or return to employee
5. Signature modal requires checkbox acknowledgment before signing
6. Rejection modal requires feedback text
7. Draft PDF can be downloaded at any stage with watermark
8. Final PDF downloads without watermark for SIGNED reviews
9. PDF contains all goals, competencies, scores, 9-grid, comments, and signatures
10. PDF uses brand colors and Tahoma font
11. All signature actions create audit log entries
12. RBAC enforced on all signature endpoints

## Out of Scope

- Email notifications (separate track)
- Calibration session signatures
- Bulk signature operations
- Electronic signature integration (DocuSign, etc.)
- PDF template customization by admins
