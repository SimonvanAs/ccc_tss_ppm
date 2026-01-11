-- TSS PPM v3.0 - Calibration Extended Tables
-- Migration: Add calibration session reviews, participants, and notes tables

-- ============================================================================
-- CALIBRATION SESSION REVIEWS (junction table)
-- Links calibration sessions to the reviews included in them
-- ============================================================================
CREATE TABLE IF NOT EXISTS calibration_session_reviews (
    session_id UUID NOT NULL REFERENCES calibration_sessions(id) ON DELETE CASCADE,
    review_id UUID NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES users(id),
    PRIMARY KEY (session_id, review_id)
);

CREATE INDEX IF NOT EXISTS idx_calibration_session_reviews_session
    ON calibration_session_reviews(session_id);
CREATE INDEX IF NOT EXISTS idx_calibration_session_reviews_review
    ON calibration_session_reviews(review_id);

-- ============================================================================
-- CALIBRATION SESSION PARTICIPANTS
-- Tracks users invited to participate in calibration sessions
-- ============================================================================
CREATE TABLE IF NOT EXISTS calibration_session_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES calibration_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL DEFAULT 'PARTICIPANT'
        CHECK (role IN ('FACILITATOR', 'PARTICIPANT', 'OBSERVER')),
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    added_by UUID REFERENCES users(id),
    UNIQUE(session_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_calibration_session_participants_session
    ON calibration_session_participants(session_id);
CREATE INDEX IF NOT EXISTS idx_calibration_session_participants_user
    ON calibration_session_participants(user_id);

-- ============================================================================
-- CALIBRATION NOTES
-- Session-level and review-level notes for calibration discussions
-- ============================================================================
CREATE TABLE IF NOT EXISTS calibration_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES calibration_sessions(id) ON DELETE CASCADE,
    review_id UUID REFERENCES reviews(id) ON DELETE CASCADE,  -- NULL for session-level notes
    content TEXT NOT NULL,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_calibration_notes_session
    ON calibration_notes(session_id);
CREATE INDEX IF NOT EXISTS idx_calibration_notes_review
    ON calibration_notes(review_id) WHERE review_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_calibration_notes_session_review
    ON calibration_notes(session_id, review_id);

-- ============================================================================
-- ADD MISSING COLUMNS TO CALIBRATION_SESSIONS (if not present)
-- ============================================================================
DO $$
BEGIN
    -- Add description column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'calibration_sessions' AND column_name = 'description'
    ) THEN
        ALTER TABLE calibration_sessions ADD COLUMN description TEXT;
    END IF;

    -- Add created_by column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'calibration_sessions' AND column_name = 'created_by'
    ) THEN
        ALTER TABLE calibration_sessions ADD COLUMN created_by UUID REFERENCES users(id);
    END IF;
END $$;
