-- TSS PPM v3.0 - Migration: Add Signature Fields
-- This migration adds signature tracking fields to the reviews table
-- Required for Review Signatures & PDF Generation feature

-- ============================================================================
-- ADD SIGNATURE BY FIELDS
-- ============================================================================
-- Track who signed the review (in case of delegation or reassignment)

ALTER TABLE reviews
ADD COLUMN IF NOT EXISTS employee_signature_by UUID REFERENCES users(id);

ALTER TABLE reviews
ADD COLUMN IF NOT EXISTS manager_signature_by UUID REFERENCES users(id);

-- ============================================================================
-- ADD REJECTION FEEDBACK FIELD
-- ============================================================================
-- Store feedback notes when a review is rejected

ALTER TABLE reviews
ADD COLUMN IF NOT EXISTS rejection_feedback TEXT;

-- ============================================================================
-- ADD INDEXES FOR SIGNATURE LOOKUPS
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_reviews_employee_signature_by ON reviews(employee_signature_by);
CREATE INDEX IF NOT EXISTS idx_reviews_manager_signature_by ON reviews(manager_signature_by);

-- ============================================================================
-- ADD COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON COLUMN reviews.employee_signature_by IS 'User ID who signed as employee (may differ from employee_id in delegation)';
COMMENT ON COLUMN reviews.manager_signature_by IS 'User ID who signed as manager (may differ from manager_id in delegation)';
COMMENT ON COLUMN reviews.rejection_feedback IS 'Feedback notes when review is rejected, requiring revision';
