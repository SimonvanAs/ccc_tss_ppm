-- TSS PPM v3.0 - Migration: Add Review Header Fields
-- This migration adds job_title and stage completion timestamps to the reviews table
-- Required for Goal Setting IDE/TOV Enhancement feature

-- ============================================================================
-- ADD JOB TITLE TO REVIEWS TABLE
-- ============================================================================
-- Job title is stored per-review since it can change annually
-- Pre-populated from previous year's review or employee profile

ALTER TABLE reviews
ADD COLUMN IF NOT EXISTS job_title VARCHAR(255);

-- ============================================================================
-- ADD STAGE COMPLETION TIMESTAMPS
-- ============================================================================
-- Track when each stage was completed (signed off)
-- These are set when the stage transitions to SIGNED status

ALTER TABLE reviews
ADD COLUMN IF NOT EXISTS goal_setting_completed_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE reviews
ADD COLUMN IF NOT EXISTS mid_year_completed_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE reviews
ADD COLUMN IF NOT EXISTS end_year_completed_at TIMESTAMP WITH TIME ZONE;

-- ============================================================================
-- ADD COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON COLUMN reviews.job_title IS 'Employee job title for this review year (can differ from user profile)';
COMMENT ON COLUMN reviews.goal_setting_completed_at IS 'Timestamp when goal setting stage was approved/signed';
COMMENT ON COLUMN reviews.mid_year_completed_at IS 'Timestamp when mid-year review was signed';
COMMENT ON COLUMN reviews.end_year_completed_at IS 'Timestamp when end-year review was signed';
