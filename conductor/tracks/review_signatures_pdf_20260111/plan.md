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

## Phase 2: Backend Signature API [checkpoint: ]

- [ ] Task: Implement review submission endpoint
  - [ ] Write tests for POST /api/v1/reviews/{id}/submit
  - [ ] Test guard conditions (goals scored, competencies scored, weights = 100%)
  - [ ] Implement endpoint with status transitions
  - [ ] Verify RBAC enforcement (manager can submit team reviews)

- [ ] Task: Implement sign review endpoint
  - [ ] Write tests for POST /api/v1/reviews/{id}/sign
  - [ ] Test employee signature flow (PENDING_EMPLOYEE_SIGNATURE → EMPLOYEE_SIGNED)
  - [ ] Test manager signature flow (PENDING_MANAGER_SIGNATURE → MANAGER_SIGNED)
  - [ ] Test auto-transition to SIGNED when both signatures present
  - [ ] Implement endpoint with timestamp recording
  - [ ] Verify RBAC enforcement

- [ ] Task: Implement reject review endpoint
  - [ ] Write tests for POST /api/v1/reviews/{id}/reject
  - [ ] Test employee rejection (PENDING_EMPLOYEE_SIGNATURE → DRAFT)
  - [ ] Test manager rejection (PENDING_MANAGER_SIGNATURE → PENDING_EMPLOYEE_SIGNATURE)
  - [ ] Test feedback note requirement
  - [ ] Implement endpoint with feedback storage
  - [ ] Verify RBAC enforcement

- [ ] Task: Implement goal setting approval flow
  - [ ] Write tests for goal submission (DRAFT → PENDING_MANAGER_SIGNATURE)
  - [ ] Write tests for manager approval (PENDING_MANAGER_SIGNATURE → SIGNED)
  - [ ] Write tests for manager rejection with feedback
  - [ ] Implement goal-specific submission logic
  - [ ] Verify weight validation (must total 100%)

- [ ] Task: Conductor - User Manual Verification 'Backend Signature API' (Protocol in workflow.md)

## Phase 3: Frontend Signature Components [checkpoint: ]

- [ ] Task: Create SignatureModal component
  - [ ] Write tests for SignatureModal rendering and interactions
  - [ ] Implement modal with summary display
  - [ ] Add checkbox acknowledgment ("I have reviewed and agree...")
  - [ ] Add Sign Review button (disabled until checkbox checked)
  - [ ] Add Cancel button
  - [ ] Style with brand colors

- [ ] Task: Create RejectionModal component
  - [ ] Write tests for RejectionModal rendering and validation
  - [ ] Implement modal with feedback text area
  - [ ] Add required validation for feedback
  - [ ] Add Submit Feedback & Return button
  - [ ] Add Cancel button
  - [ ] Style with brand colors

- [ ] Task: Create SignatureStatus component
  - [ ] Write tests for SignatureStatus display states
  - [ ] Implement status badge display (Awaiting Signature, Signed, etc.)
  - [ ] Show signature timestamps when signed
  - [ ] Show signer information
  - [ ] Style with brand colors

- [ ] Task: Integrate signature UI into ReviewView
  - [ ] Write tests for signature button visibility by role and status
  - [ ] Add Submit for Signature button (manager, DRAFT status)
  - [ ] Add Sign Review button (appropriate role/status)
  - [ ] Add Reject button (appropriate role/status)
  - [ ] Connect to API endpoints
  - [ ] Handle loading and error states

- [ ] Task: Conductor - User Manual Verification 'Frontend Signature Components' (Protocol in workflow.md)

## Phase 4: PDF Generation Service [checkpoint: ]

- [ ] Task: Create PDF template with WeasyPrint
  - [ ] Write tests for PDF template rendering
  - [ ] Create HTML/CSS template for review PDF
  - [ ] Implement header section (logo, employee info, review year)
  - [ ] Implement goals section with scores and comments
  - [ ] Implement competencies section with scores
  - [ ] Apply brand styling (Magenta, Navy Blue, Tahoma)

- [ ] Task: Implement 9-grid visualization for PDF
  - [ ] Write tests for 9-grid SVG/HTML generation
  - [ ] Create 3x3 grid with color coding
  - [ ] Mark employee position on grid
  - [ ] Ensure proper rendering in PDF

- [ ] Task: Implement signature and comments sections
  - [ ] Write tests for signature section rendering
  - [ ] Add employee signature line with timestamp
  - [ ] Add manager signature line with timestamp
  - [ ] Add comments section (manager, employee, feedback)
  - [ ] Handle "Pending" state for unsigned

- [ ] Task: Implement draft watermark
  - [ ] Write tests for watermark presence/absence
  - [ ] Add "DRAFT" watermark for non-SIGNED reviews
  - [ ] Remove watermark for SIGNED reviews
  - [ ] Ensure watermark doesn't obscure content

- [ ] Task: Implement PDF generation endpoint
  - [ ] Write tests for GET /api/v1/reviews/{id}/pdf
  - [ ] Test draft PDF generation (any status)
  - [ ] Test final PDF generation (SIGNED status)
  - [ ] Implement endpoint with WeasyPrint integration
  - [ ] Verify PDF-A format output
  - [ ] Verify RBAC enforcement
  - [ ] Test performance (< 5 seconds)

- [ ] Task: Conductor - User Manual Verification 'PDF Generation Service' (Protocol in workflow.md)

## Phase 5: Frontend PDF Download [checkpoint: ]

- [ ] Task: Create PDFDownloadButton component
  - [ ] Write tests for button label by review status
  - [ ] Implement "Download Draft PDF" for non-SIGNED
  - [ ] Implement "Download Final Report" for SIGNED
  - [ ] Add loading state during generation
  - [ ] Handle download response

- [ ] Task: Integrate PDF download into ReviewView
  - [ ] Write tests for PDF button visibility
  - [ ] Add PDFDownloadButton to review UI
  - [ ] Position appropriately in layout
  - [ ] Test download flow end-to-end

- [ ] Task: Conductor - User Manual Verification 'Frontend PDF Download' (Protocol in workflow.md)

## Phase 6: Multi-language PDF Support [checkpoint: ]

- [ ] Task: Implement i18n for PDF content
  - [ ] Write tests for PDF in each language (EN/NL/ES)
  - [ ] Add translation keys for PDF labels
  - [ ] Pass user language preference to PDF generator
  - [ ] Verify competency names render in correct language
  - [ ] Verify all static text translated

- [ ] Task: Conductor - User Manual Verification 'Multi-language PDF Support' (Protocol in workflow.md)

## Phase 7: Integration Testing & Polish [checkpoint: ]

- [ ] Task: End-to-end signature flow testing
  - [ ] Test complete goal setting approval flow
  - [ ] Test complete mid-year signature flow
  - [ ] Test complete end-year signature flow
  - [ ] Test rejection and re-submission flows
  - [ ] Verify audit logs for all actions

- [ ] Task: End-to-end PDF testing
  - [ ] Test PDF generation at each review status
  - [ ] Verify PDF content accuracy
  - [ ] Test PDF in all three languages
  - [ ] Verify performance requirements met

- [ ] Task: Conductor - User Manual Verification 'Integration Testing & Polish' (Protocol in workflow.md)
