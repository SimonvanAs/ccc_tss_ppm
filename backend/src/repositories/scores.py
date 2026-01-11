# TSS PPM v3.0 - Scores Repository
"""Database operations for goal and competency scores."""

from typing import Any, Dict, List, Optional
from uuid import UUID

import asyncpg


class ScoresRepository:
    """Repository for score database operations."""

    def __init__(self, conn: asyncpg.Connection):
        """Initialize repository with database connection.

        Args:
            conn: Async PostgreSQL connection
        """
        self.conn = conn

    async def get_goal_scores(self, review_id: UUID) -> List[Dict[str, Any]]:
        """Get all goal scores for a review.

        Args:
            review_id: The review UUID

        Returns:
            List of goal records with scores
        """
        query = """
            SELECT
                g.id,
                g.review_id,
                g.title,
                g.description,
                g.goal_type,
                g.weight,
                g.score,
                g.change_reason AS feedback,
                g.display_order
            FROM goals g
            WHERE g.review_id = $1 AND g.deleted_at IS NULL
            ORDER BY g.display_order ASC
        """
        rows = await self.conn.fetch(query, review_id)
        return [dict(row) for row in rows]

    async def get_competency_scores(
        self, review_id: UUID, language: str = 'en'
    ) -> List[Dict[str, Any]]:
        """Get all competency scores for a review.

        Args:
            review_id: The review UUID
            language: Language code for titles (en, nl, es)

        Returns:
            List of competency score records with competency metadata
        """
        # Build dynamic title column based on language
        title_col = f'title_{language}' if language in ('en', 'nl', 'es') else 'title_en'

        query = f"""
            SELECT
                cs.id,
                cs.review_id,
                cs.competency_id,
                cs.score,
                cs.notes,
                c.category,
                c.subcategory,
                c.{title_col} AS title_en,
                c.display_order
            FROM competency_scores cs
            JOIN competencies c ON c.id = cs.competency_id
            WHERE cs.review_id = $1
            ORDER BY c.category, c.display_order
        """
        rows = await self.conn.fetch(query, review_id)
        return [dict(row) for row in rows]

    async def get_all_scores(
        self, review_id: UUID, language: str = 'en'
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get both goal and competency scores for a review.

        Args:
            review_id: The review UUID
            language: Language code for competency titles

        Returns:
            Dictionary with 'goal_scores' and 'competency_scores' lists
        """
        goal_scores = await self.get_goal_scores(review_id)
        competency_scores = await self.get_competency_scores(review_id, language)

        return {
            'goal_scores': goal_scores,
            'competency_scores': competency_scores,
        }

    def _validate_score(self, score: int) -> None:
        """Validate that score is in valid range (1-3).

        Args:
            score: The score value to validate

        Raises:
            ValueError: If score is not between 1 and 3
        """
        if score < 1 or score > 3:
            raise ValueError(f'Score must be between 1 and 3, got {score}')

    async def upsert_goal_score(
        self,
        goal_id: UUID,
        score: int,
        feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update a goal's score and feedback.

        Args:
            goal_id: The goal UUID
            score: Score value (1-3)
            feedback: Optional feedback text

        Returns:
            Updated goal record

        Raises:
            ValueError: If score is not between 1 and 3
        """
        self._validate_score(score)

        query = """
            UPDATE goals
            SET score = $1, change_reason = $2, updated_at = NOW()
            WHERE id = $3 AND deleted_at IS NULL
            RETURNING id, review_id, title, description, goal_type,
                      weight, score, change_reason AS feedback, display_order
        """
        row = await self.conn.fetchrow(query, score, feedback, goal_id)
        return dict(row) if row else None

    async def upsert_competency_score(
        self,
        review_id: UUID,
        competency_id: UUID,
        score: int,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Insert or update a competency score.

        Args:
            review_id: The review UUID
            competency_id: The competency UUID
            score: Score value (1-3)
            notes: Optional notes text

        Returns:
            Upserted competency score record

        Raises:
            ValueError: If score is not between 1 and 3
        """
        self._validate_score(score)

        query = """
            INSERT INTO competency_scores (review_id, competency_id, score, notes)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (review_id, competency_id)
            DO UPDATE SET score = $3, notes = $4, updated_at = NOW()
            RETURNING id, review_id, competency_id, score, notes
        """
        row = await self.conn.fetchrow(query, review_id, competency_id, score, notes)
        return dict(row) if row else None

    async def bulk_upsert_goal_scores(
        self, goal_scores: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Update multiple goal scores at once.

        Args:
            goal_scores: List of dicts with goal_id, score, and optional feedback

        Returns:
            List of updated goal records
        """
        results = []
        for gs in goal_scores:
            result = await self.upsert_goal_score(
                goal_id=gs['goal_id'],
                score=gs['score'],
                feedback=gs.get('feedback'),
            )
            if result:
                results.append(result)
        return results

    async def bulk_upsert_competency_scores(
        self, review_id: UUID, competency_scores: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Update multiple competency scores at once.

        Args:
            review_id: The review UUID
            competency_scores: List of dicts with competency_id, score, optional notes

        Returns:
            List of upserted competency score records
        """
        results = []
        for cs in competency_scores:
            result = await self.upsert_competency_score(
                review_id=review_id,
                competency_id=cs['competency_id'],
                score=cs['score'],
                notes=cs.get('notes'),
            )
            if result:
                results.append(result)
        return results
