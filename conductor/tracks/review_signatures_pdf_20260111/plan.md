# Plan: Review Signatures & PDF Generation

## Phase 1: Database Schema & Models [checkpoint: 5ff9c04]

- [x] Task: Add signature fields to reviews table `5b99607`
  - [x] Write migration SQL for employee_signature_by, manager_signature_by columns
  - [x] Add rejection_feedback column for storing feedback notes
  - [x] Run migration and verify schema
  - Note: employee_signature_date and manager_signature_date already exist

- [x] Task: Create signature audit log entries `869bbc2`
  - [x] Write tests for signature audit log creation
  - [x] Implement audit log entries for sign/reject actions
  - [x] Verify audit logs capture user_id, action, timestamp, review_id

- [x] Task: Conductor - User Manual Verification 'Database Schema & Models' (Protocol in workflow.md)

## Phase 2: Backend Signature API [checkpoint: bba7ba0]

- [x] Task: Implement review submission endpoint `existing`
  - [x] Write tests for POST /api/v1/reviews/{id}/submit
  - [x] Test guard conditions (goals scored, competencies scored, weights = 100%)
  - [x] Implement endpoint with status transitions
  - [x] Verify RBAC enforcement (manager can submit team reviews)
  - Note: submit-scores endpoint already exists with audit logging

- [x] Task: Implement sign review endpoint `16ee0a0`
  - [x] Write tests for POST /api/v1/reviews/{id}/sign
  - [x] Test employee signature flow (PENDING_EMPLOYEE_SIGNATURE → PENDING_MANAGER_SIGNATURE)
  - [x] Test manager signature flow (PENDING_MANAGER_SIGNATURE → SIGNED)
  - [x] Test auto-transition to SIGNED when both signatures present
  - [x] Implement endpoint with timestamp recording
  - [x] Verify RBAC enforcement

- [x] Task: Implement reject review endpoint `c44ac9d`
  - [x] Write tests for POST /api/v1/reviews/{id}/reject
  - [x] Test employee rejection (PENDING_EMPLOYEE_SIGNATURE → DRAFT)
  - [x] Test manager rejection (PENDING_MANAGER_SIGNATURE → PENDING_EMPLOYEE_SIGNATURE)
  - [x] Test feedback note requirement
  - [x] Implement endpoint with feedback storage
  - [x] Verify RBAC enforcement

- [x] Task: Implement goal setting approval flow `86a84a3`
  - [x] Write tests for goal submission (DRAFT → PENDING_MANAGER_SIGNATURE)
  - [x] Write tests for manager approval (PENDING_MANAGER_SIGNATURE → SIGNED)
  - [x] Write tests for manager rejection with feedback
  - [x] Implement goal-specific submission logic
  - [x] Verify weight validation (must total 100%)
  - Note: Uses existing submit_review/sign/reject endpoints with stage awareness

- [x] Task: Conductor - User Manual Verification 'Backend Signature API' (Protocol in workflow.md)

## Phase 3: Frontend Signature Components [checkpoint: 1de901e]

- [x] Task: Create SignatureModal component `a65a313`
  - [x] Write tests for SignatureModal rendering and interactions
  - [x] Implement modal with summary display
  - [x] Add checkbox acknowledgment ("I have reviewed and agree...")
  - [x] Add Sign Review button (disabled until checkbox checked)
  - [x] Add Cancel button
  - [x] Style with brand colors

- [x] Task: Create RejectionModal component
  - [x] Write tests for RejectionModal rendering and validation
  - [x] Implement modal with feedback text area
  - [x] Add required validation for feedback
  - [x] Add Submit Feedback & Return button
  - [x] Add Cancel button
  - [x] Style with brand colors

- [x] Task: Create SignatureStatus component
  - [x] Write tests for SignatureStatus display states
  - [x] Implement status badge display (Awaiting Signature, Signed, etc.)
  - [x] Show signature timestamps when signed
  - [x] Show signer information
  - [x] Style with brand colors

- [x] Task: Integrate signature UI into ReviewView
  - [x] Write tests for signature button visibility by role and status
  - [x] Add Submit for Signature button (manager, DRAFT status)
  - [x] Add Sign Review button (appropriate role/status)
  - [x] Add Reject button (appropriate role/status)
  - [x] Connect to API endpoints
  - [x] Handle loading and error states

- [ ] Task: Conductor - User Manual Verification 'Frontend Signature Components' (Protocol in workflow.md)

## Phase 4: PDF Generation Service [checkpoint: 22e358b]

- [x] Task: Create PDF template with WeasyPrint
  - [x] Write tests for PDF template rendering
  - [x] Create HTML/CSS template for review PDF
  - [x] Implement header section (logo, employee info, review year)
  - [x] Implement goals section with scores and comments
  - [x] Implement competencies section with scores
  - [x] Apply brand styling (Magenta, Navy Blue, Tahoma)

- [x] Task: Implement 9-grid visualization for PDF
  - [x] Write tests for 9-grid SVG/HTML generation
  - [x] Create 3x3 grid with color coding
  - [x] Mark employee position on grid
  - [x] Ensure proper rendering in PDF

- [x] Task: Implement signature and comments sections
  - [x] Write tests for signature section rendering
  - [x] Add employee signature line with timestamp
  - [x] Add manager signature line with timestamp
  - [x] Add comments section (manager, employee, feedback)
  - [x] Handle "Pending" state for unsigned

- [x] Task: Implement draft watermark
  - [x] Write tests for watermark presence/absence
  - [x] Add "DRAFT" watermark for non-SIGNED reviews
  - [x] Remove watermark for SIGNED reviews
  - [x] Ensure watermark doesn't obscure content

- [x] Task: Implement PDF generation endpoint
  - [x] Write tests for GET /api/v1/reviews/{id}/pdf
  - [x] Test draft PDF generation (any status)
  - [x] Test final PDF generation (SIGNED status)
  - [x] Implement endpoint with WeasyPrint integration
  - [x] Verify PDF-A format output
  - [x] Verify RBAC enforcement
  - [x] Test performance (< 5 seconds)

- [ ] Task: Conductor - User Manual Verification 'PDF Generation Service' (Protocol in workflow.md)

## Phase 5: Frontend PDF Download [checkpoint: e48801e]

- [x] Task: Create PDFDownloadButton component
  - [x] Write tests for button label by review status
  - [x] Implement "Download Draft PDF" for non-SIGNED
  - [x] Implement "Download Final Report" for SIGNED
  - [x] Add loading state during generation
  - [x] Handle download response

- [x] Task: Integrate PDF download into ReviewView
  - [x] Write tests for PDF button visibility
  - [x] Add PDFDownloadButton to review UI
  - [x] Position appropriately in layout
  - [x] Test download flow end-to-end

- [ ] Task: Conductor - User Manual Verification 'Frontend PDF Download' (Protocol in workflow.md)

## Phase 6: Multi-language PDF Support [checkpoint: 5be67ae]

- [x] Task: Implement i18n for PDF content
  - [x] Write tests for PDF in each language (EN/NL/ES)
  - [x] Add translation keys for PDF labels
  - [x] Pass user language preference to PDF generator
  - [x] Verify competency names render in correct language
  - [x] Verify all static text translated

- [ ] Task: Conductor - User Manual Verification 'Multi-language PDF Support' (Protocol in workflow.md)

## Phase 7: Integration Testing & Polish [checkpoint: ]

- [x] Task: End-to-end signature flow testing
  - [x] Test complete goal setting approval flow
  - [x] Test complete mid-year signature flow
  - [x] Test complete end-year signature flow
  - [x] Test rejection and re-submission flows
  - [x] Verify audit logs for all actions

- [x] Task: End-to-end PDF testing
  - [x] Test PDF generation at each review status
  - [x] Verify PDF content accuracy
  - [x] Test PDF in all three languages
  - [x] Verify performance requirements met

- [ ] Task: Conductor - User Manual Verification 'Integration Testing & Polish' (Protocol in workflow.md)
