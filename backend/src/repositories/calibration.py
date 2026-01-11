# TSS PPM v3.0 - Calibration Repository
"""Database operations for calibration sessions."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

import asyncpg


class CalibrationRepository:
    """Repository for calibration session database operations."""

    # Valid status values
    VALID_STATUSES = ['PREPARATION', 'IN_PROGRESS', 'PENDING_APPROVAL', 'COMPLETED', 'CANCELLED']

    # Status transitions
    STATUS_TRANSITIONS = {
        'PREPARATION': ['IN_PROGRESS', 'CANCELLED'],
        'IN_PROGRESS': ['PENDING_APPROVAL', 'COMPLETED', 'CANCELLED'],
        'PENDING_APPROVAL': ['COMPLETED', 'IN_PROGRESS', 'CANCELLED'],
        'COMPLETED': [],  # Terminal state
        'CANCELLED': [],  # Terminal state
    }

    def __init__(self, conn: asyncpg.Connection):
        """Initialize repository with database connection.

        Args:
            conn: Async PostgreSQL connection
        """
        self.conn = conn

    # --- Session CRUD ---

    async def create_session(
        self,
        opco_id: UUID,
        name: str,
        review_year: int,
        scope: str,
        created_by: UUID,
        description: Optional[str] = None,
        business_unit_id: Optional[UUID] = None,
        facilitator_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Create a new calibration session.

        Args:
            opco_id: Operating company ID
            name: Session name
            review_year: Year of reviews to calibrate
            scope: 'BUSINESS_UNIT' or 'COMPANY_WIDE'
            created_by: User ID who created the session
            description: Optional session description
            business_unit_id: Optional business unit ID (required if scope is BUSINESS_UNIT)
            facilitator_id: Optional facilitator user ID

        Returns:
            The created session record
        """
        query = """
            INSERT INTO calibration_sessions (
                opco_id, name, description, review_year, scope,
                business_unit_id, facilitator_id, created_by, status
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'PREPARATION')
            RETURNING *
        """
        row = await self.conn.fetchrow(
            query, opco_id, name, description, review_year, scope,
            business_unit_id, facilitator_id, created_by
        )
        return dict(row) if row else None

    async def get_session_by_id(
        self,
        session_id: UUID,
        opco_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a calibration session by ID.

        Args:
            session_id: The session UUID
            opco_id: Optional OpCo ID for isolation

        Returns:
            Session record or None if not found
        """
        if opco_id:
            query = """
                SELECT * FROM calibration_sessions
                WHERE id = $1 AND opco_id = $2
            """
            row = await self.conn.fetchrow(query, session_id, opco_id)
        else:
            query = "SELECT * FROM calibration_sessions WHERE id = $1"
            row = await self.conn.fetchrow(query, session_id)

        return dict(row) if row else None

    async def list_sessions(
        self,
        opco_id: UUID,
        status: Optional[str] = None,
        review_year: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List calibration sessions for an OpCo.

        Args:
            opco_id: Operating company ID
            status: Optional status filter
            review_year: Optional year filter

        Returns:
            List of session records
        """
        conditions = ["opco_id = $1"]
        params: List[Any] = [opco_id]
        param_idx = 2

        if status:
            conditions.append(f"status = ${param_idx}")
            params.append(status)
            param_idx += 1

        if review_year:
            conditions.append(f"review_year = ${param_idx}")
            params.append(review_year)
            param_idx += 1

        where_clause = " AND ".join(conditions)
        query = f"""
            SELECT * FROM calibration_sessions
            WHERE {where_clause}
            ORDER BY created_at DESC
        """
        rows = await self.conn.fetch(query, *params)
        return [dict(row) for row in rows]

    async def update_session(
        self,
        session_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        facilitator_id: Optional[UUID] = None,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update a calibration session.

        Args:
            session_id: The session UUID
            name: New name (optional)
            description: New description (optional)
            facilitator_id: New facilitator (optional)
            notes: New notes (optional)

        Returns:
            Updated session record or None if not found
        """
        updates = []
        params: List[Any] = []
        param_idx = 1

        if name is not None:
            updates.append(f"name = ${param_idx}")
            params.append(name)
            param_idx += 1

        if description is not None:
            updates.append(f"description = ${param_idx}")
            params.append(description)
            param_idx += 1

        if facilitator_id is not None:
            updates.append(f"facilitator_id = ${param_idx}")
            params.append(facilitator_id)
            param_idx += 1

        if notes is not None:
            updates.append(f"notes = ${param_idx}")
            params.append(notes)
            param_idx += 1

        if not updates:
            return await self.get_session_by_id(session_id)

        updates.append("updated_at = NOW()")
        params.append(session_id)

        set_clause = ", ".join(updates)
        query = f"""
            UPDATE calibration_sessions
            SET {set_clause}
            WHERE id = ${param_idx}
            RETURNING *
        """
        row = await self.conn.fetchrow(query, *params)
        return dict(row) if row else None

    async def delete_session(self, session_id: UUID) -> bool:
        """Delete a calibration session (only if in PREPARATION status).

        Args:
            session_id: The session UUID

        Returns:
            True if deleted, False otherwise
        """
        # First check status
        session = await self.get_session_by_id(session_id)
        if not session:
            return False

        if session['status'] != 'PREPARATION':
            return False

        await self.conn.execute(
            "DELETE FROM calibration_sessions WHERE id = $1",
            session_id
        )
        return True

    # --- Status Transitions ---

    async def start_session(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        """Transition session from PREPARATION to IN_PROGRESS.

        Args:
            session_id: The session UUID

        Returns:
            Updated session or None if transition not allowed
        """
        session = await self.get_session_by_id(session_id)
        if not session or session['status'] != 'PREPARATION':
            return None

        query = """
            UPDATE calibration_sessions
            SET status = 'IN_PROGRESS', updated_at = NOW()
            WHERE id = $1
            RETURNING *
        """
        row = await self.conn.fetchrow(query, session_id)
        return dict(row) if row else None

    async def complete_session(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        """Transition session to COMPLETED status.

        Args:
            session_id: The session UUID

        Returns:
            Updated session or None if transition not allowed
        """
        session = await self.get_session_by_id(session_id)
        if not session or session['status'] not in ['IN_PROGRESS', 'PENDING_APPROVAL']:
            return None

        query = """
            UPDATE calibration_sessions
            SET status = 'COMPLETED', completed_at = NOW(), updated_at = NOW()
            WHERE id = $1
            RETURNING *
        """
        row = await self.conn.fetchrow(query, session_id)
        return dict(row) if row else None

    # --- Review Management ---

    async def add_review_to_session(
        self,
        session_id: UUID,
        review_id: UUID,
        added_by: UUID
    ) -> bool:
        """Add a review to a calibration session.

        Args:
            session_id: The session UUID
            review_id: The review UUID
            added_by: User ID who added the review

        Returns:
            True if added successfully
        """
        query = """
            INSERT INTO calibration_session_reviews (session_id, review_id, added_by)
            VALUES ($1, $2, $3)
            ON CONFLICT (session_id, review_id) DO NOTHING
        """
        await self.conn.execute(query, session_id, review_id, added_by)
        return True

    async def remove_review_from_session(
        self,
        session_id: UUID,
        review_id: UUID
    ) -> bool:
        """Remove a review from a calibration session.

        Args:
            session_id: The session UUID
            review_id: The review UUID

        Returns:
            True if removed successfully
        """
        query = """
            DELETE FROM calibration_session_reviews
            WHERE session_id = $1 AND review_id = $2
        """
        await self.conn.execute(query, session_id, review_id)
        return True

    async def get_session_reviews(
        self,
        session_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all reviews in a calibration session with scores.

        Args:
            session_id: The session UUID

        Returns:
            List of review records with employee info and scores
        """
        query = """
            SELECT
                r.id AS review_id,
                r.employee_id,
                CONCAT(u.first_name, ' ', u.last_name) AS employee_name,
                u.email AS employee_email,
                r.what_score,
                r.how_score,
                r.grid_position_what,
                r.grid_position_how,
                r.what_veto_active,
                r.how_veto_active,
                r.status AS review_status,
                m.first_name AS manager_first_name,
                m.last_name AS manager_last_name
            FROM calibration_session_reviews csr
            JOIN reviews r ON r.id = csr.review_id
            JOIN users u ON u.id = r.employee_id
            LEFT JOIN users m ON m.id = r.manager_id
            WHERE csr.session_id = $1
            ORDER BY u.last_name, u.first_name
        """
        rows = await self.conn.fetch(query, session_id)
        return [dict(row) for row in rows]

    # --- Participant Management ---

    async def add_participant(
        self,
        session_id: UUID,
        user_id: UUID,
        role: str,
        added_by: UUID
    ) -> Optional[Dict[str, Any]]:
        """Add a participant to a calibration session.

        Args:
            session_id: The session UUID
            user_id: The user UUID to add
            role: Participant role (FACILITATOR, PARTICIPANT, OBSERVER)
            added_by: User ID who added the participant

        Returns:
            The created participant record
        """
        query = """
            INSERT INTO calibration_session_participants (session_id, user_id, role, added_by)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (session_id, user_id) DO UPDATE SET role = $3
            RETURNING *
        """
        row = await self.conn.fetchrow(query, session_id, user_id, role, added_by)
        return dict(row) if row else None

    async def remove_participant(
        self,
        session_id: UUID,
        user_id: UUID
    ) -> bool:
        """Remove a participant from a calibration session.

        Args:
            session_id: The session UUID
            user_id: The user UUID to remove

        Returns:
            True if removed successfully
        """
        query = """
            DELETE FROM calibration_session_participants
            WHERE session_id = $1 AND user_id = $2
        """
        await self.conn.execute(query, session_id, user_id)
        return True

    async def get_session_participants(
        self,
        session_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all participants in a calibration session.

        Args:
            session_id: The session UUID

        Returns:
            List of participant records with user info
        """
        query = """
            SELECT
                csp.user_id,
                csp.role,
                u.first_name,
                u.last_name,
                u.email
            FROM calibration_session_participants csp
            JOIN users u ON u.id = csp.user_id
            WHERE csp.session_id = $1
            ORDER BY csp.role, u.last_name
        """
        rows = await self.conn.fetch(query, session_id)
        return [dict(row) for row in rows]

    # --- Notes Management ---

    async def add_note(
        self,
        session_id: UUID,
        content: str,
        created_by: UUID,
        review_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Add a note to a calibration session.

        Args:
            session_id: The session UUID
            content: Note content
            created_by: User ID who created the note
            review_id: Optional review UUID for review-level notes

        Returns:
            The created note record
        """
        query = """
            INSERT INTO calibration_notes (session_id, review_id, content, created_by)
            VALUES ($1, $2, $3, $4)
            RETURNING *
        """
        row = await self.conn.fetchrow(query, session_id, review_id, content, created_by)
        return dict(row) if row else None

    async def get_session_notes(
        self,
        session_id: UUID,
        review_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get notes for a calibration session.

        Args:
            session_id: The session UUID
            review_id: Optional review UUID to filter notes

        Returns:
            List of note records
        """
        if review_id:
            query = """
                SELECT cn.*, u.first_name, u.last_name
                FROM calibration_notes cn
                JOIN users u ON u.id = cn.created_by
                WHERE cn.session_id = $1 AND cn.review_id = $2
                ORDER BY cn.created_at DESC
            """
            rows = await self.conn.fetch(query, session_id, review_id)
        else:
            query = """
                SELECT cn.*, u.first_name, u.last_name
                FROM calibration_notes cn
                JOIN users u ON u.id = cn.created_by
                WHERE cn.session_id = $1
                ORDER BY cn.created_at DESC
            """
            rows = await self.conn.fetch(query, session_id)

        return [dict(row) for row in rows]

    # --- Score Adjustment ---

    async def get_review_current_scores(
        self,
        review_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Get the current scores for a review.

        Args:
            review_id: The review UUID

        Returns:
            Review scores or None if not found
        """
        query = """
            SELECT id, what_score, how_score, grid_position_what, grid_position_how
            FROM reviews
            WHERE id = $1
        """
        row = await self.conn.fetchrow(query, review_id)
        return dict(row) if row else None

    async def is_review_in_session(
        self,
        session_id: UUID,
        review_id: UUID
    ) -> bool:
        """Check if a review is part of a calibration session.

        Args:
            session_id: The session UUID
            review_id: The review UUID

        Returns:
            True if the review is in the session
        """
        query = """
            SELECT 1 FROM calibration_session_reviews
            WHERE session_id = $1 AND review_id = $2
        """
        row = await self.conn.fetchrow(query, session_id, review_id)
        return row is not None

    async def adjust_review_scores(
        self,
        session_id: UUID,
        review_id: UUID,
        what_score: Optional[Any],
        how_score: Optional[Any],
        adjusted_by: UUID,
        rationale: str,
    ) -> Optional[Dict[str, Any]]:
        """Adjust review scores during calibration and create audit trail.

        Args:
            session_id: The session UUID
            review_id: The review UUID
            what_score: New WHAT score (optional)
            how_score: New HOW score (optional)
            adjusted_by: User ID making the adjustment
            rationale: Required explanation for the adjustment

        Returns:
            The adjustment record
        """
        # Get current scores
        current = await self.get_review_current_scores(review_id)
        if not current:
            return None

        # Calculate new grid positions (1.00-1.66 -> 1, 1.67-2.33 -> 2, 2.34-3.00 -> 3)
        def score_to_grid(score):
            if score is None:
                return None
            score_float = float(score)
            if score_float < 1.67:
                return 1
            elif score_float < 2.34:
                return 2
            else:
                return 3

        new_what_score = what_score if what_score is not None else current['what_score']
        new_how_score = how_score if how_score is not None else current['how_score']
        new_grid_what = score_to_grid(new_what_score)
        new_grid_how = score_to_grid(new_how_score)

        # Create audit trail entry
        audit_query = """
            INSERT INTO calibration_adjustments (
                session_id, review_id, adjusted_by,
                original_what_score, original_how_score,
                original_grid_what, original_grid_how,
                adjusted_what_score, adjusted_how_score,
                adjusted_grid_what, adjusted_grid_how,
                adjustment_notes
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            RETURNING *
        """
        adjustment = await self.conn.fetchrow(
            audit_query,
            session_id, review_id, adjusted_by,
            current['what_score'], current['how_score'],
            current['grid_position_what'], current['grid_position_how'],
            new_what_score, new_how_score,
            new_grid_what, new_grid_how,
            rationale,
        )

        # Update review scores
        update_query = """
            UPDATE reviews
            SET what_score = $1,
                how_score = $2,
                grid_position_what = $3,
                grid_position_how = $4,
                updated_at = NOW()
            WHERE id = $5
        """
        await self.conn.execute(
            update_query,
            new_what_score, new_how_score,
            new_grid_what, new_grid_how,
            review_id,
        )

        return dict(adjustment) if adjustment else None

    async def get_review_adjustments(
        self,
        session_id: UUID,
        review_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get adjustment history for a review in a session.

        Args:
            session_id: The session UUID
            review_id: The review UUID

        Returns:
            List of adjustment records with adjuster info
        """
        query = """
            SELECT ca.*, u.first_name AS adjuster_first_name, u.last_name AS adjuster_last_name
            FROM calibration_adjustments ca
            JOIN users u ON u.id = ca.adjusted_by
            WHERE ca.session_id = $1 AND ca.review_id = $2
            ORDER BY ca.created_at DESC
        """
        rows = await self.conn.fetch(query, session_id, review_id)
        return [dict(row) for row in rows]
