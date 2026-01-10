# TSS PPM v3.0 - Goal Repository
"""Database operations for goals."""

from typing import Any, Dict, List, Optional
from uuid import UUID

import asyncpg

from src.schemas.goal import GoalCreate


class GoalRepository:
    """Repository for goal database operations."""

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def get_goals_by_review(self, review_id: UUID) -> List[Dict[str, Any]]:
        """Get all goals for a review, ordered by display_order.

        Args:
            review_id: The review UUID

        Returns:
            List of goal records
        """
        query = """
            SELECT id, review_id, title, description, goal_type,
                   weight, score, display_order
            FROM goals
            WHERE review_id = $1 AND deleted_at IS NULL
            ORDER BY display_order ASC
        """
        rows = await self.conn.fetch(query, review_id)
        return [dict(row) for row in rows]

    async def get_goal(self, goal_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a single goal by ID.

        Args:
            goal_id: The goal UUID

        Returns:
            Goal record or None if not found
        """
        query = """
            SELECT id, review_id, title, description, goal_type,
                   weight, score, display_order
            FROM goals
            WHERE id = $1 AND deleted_at IS NULL
        """
        row = await self.conn.fetchrow(query, goal_id)
        return dict(row) if row else None

    async def create_goal(
        self, review_id: UUID, goal_data: GoalCreate
    ) -> Dict[str, Any]:
        """Create a new goal.

        Args:
            review_id: The review UUID
            goal_data: Goal creation data

        Returns:
            Created goal record
        """
        # Get next display_order
        next_order = await self.conn.fetchval(
            """
            SELECT COALESCE(MAX(display_order), -1) + 1
            FROM goals
            WHERE review_id = $1 AND deleted_at IS NULL
            """,
            review_id,
        )

        query = """
            INSERT INTO goals (review_id, title, description, goal_type, weight, display_order)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, review_id, title, description, goal_type, weight, score, display_order
        """
        row = await self.conn.fetchrow(
            query,
            review_id,
            goal_data.title,
            goal_data.description,
            goal_data.goal_type.value,
            goal_data.weight,
            next_order,
        )
        return dict(row)

    async def update_goal(
        self, goal_id: UUID, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing goal.

        Args:
            goal_id: The goal UUID
            updates: Dictionary of fields to update

        Returns:
            Updated goal record or None if not found
        """
        if not updates:
            return await self.get_goal(goal_id)

        # Build dynamic UPDATE query
        set_clauses = []
        values = []
        param_num = 1

        for key, value in updates.items():
            if key in ('title', 'description', 'goal_type', 'weight', 'score'):
                set_clauses.append(f"{key} = ${param_num}")
                values.append(value.value if hasattr(value, 'value') else value)
                param_num += 1

        if not set_clauses:
            return await self.get_goal(goal_id)

        # Add updated_at
        set_clauses.append(f"updated_at = NOW()")

        values.append(goal_id)

        query = f"""
            UPDATE goals
            SET {', '.join(set_clauses)}
            WHERE id = ${param_num} AND deleted_at IS NULL
            RETURNING id, review_id, title, description, goal_type, weight, score, display_order
        """

        row = await self.conn.fetchrow(query, *values)
        return dict(row) if row else None

    async def delete_goal(self, goal_id: UUID) -> bool:
        """Soft delete a goal.

        Args:
            goal_id: The goal UUID

        Returns:
            True if goal was deleted, False if not found
        """
        result = await self.conn.execute(
            """
            UPDATE goals
            SET deleted_at = NOW()
            WHERE id = $1 AND deleted_at IS NULL
            """,
            goal_id,
        )
        return result == 'UPDATE 1'

    async def reorder_goals(self, review_id: UUID, goal_ids: List[UUID]) -> None:
        """Reorder goals by updating their display_order.

        Args:
            review_id: The review UUID
            goal_ids: List of goal UUIDs in the desired order
        """
        for order, goal_id in enumerate(goal_ids):
            await self.conn.execute(
                """
                UPDATE goals
                SET display_order = $1, updated_at = NOW()
                WHERE id = $2 AND review_id = $3 AND deleted_at IS NULL
                """,
                order,
                goal_id,
                review_id,
            )

    async def get_weight_total(self, review_id: UUID) -> int:
        """Get the sum of all goal weights for a review.

        Args:
            review_id: The review UUID

        Returns:
            Total weight (0 if no goals)
        """
        result = await self.conn.fetchval(
            """
            SELECT COALESCE(SUM(weight), 0)
            FROM goals
            WHERE review_id = $1 AND deleted_at IS NULL
            """,
            review_id,
        )
        return result or 0

    async def get_goal_count(self, review_id: UUID) -> int:
        """Get the count of goals for a review.

        Args:
            review_id: The review UUID

        Returns:
            Number of goals
        """
        result = await self.conn.fetchval(
            """
            SELECT COUNT(*)
            FROM goals
            WHERE review_id = $1 AND deleted_at IS NULL
            """,
            review_id,
        )
        return result or 0
