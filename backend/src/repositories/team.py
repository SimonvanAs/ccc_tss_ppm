# TSS PPM v3.0 - Team Repository
"""Database operations for manager team members."""

from typing import Any, Dict, List, Optional
from uuid import UUID

import asyncpg


class TeamRepository:
    """Repository for team member database operations."""

    # Standard number of competencies per TOV level
    COMPETENCIES_PER_LEVEL = 6

    def __init__(self, conn: asyncpg.Connection):
        """Initialize repository with database connection.

        Args:
            conn: Async PostgreSQL connection
        """
        self.conn = conn

    async def get_team_members_by_manager_id(
        self, manager_id: UUID, review_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all team members for a manager with their review information.

        Args:
            manager_id: The manager's user UUID
            review_year: Optional filter for specific review year

        Returns:
            List of team member records with review data
        """
        query = """
            SELECT
                u.id,
                u.email,
                u.first_name,
                u.last_name,
                u.function_title,
                u.tov_level,
                r.id AS review_id,
                r.stage AS review_stage,
                r.status AS review_status,
                COALESCE((
                    SELECT COUNT(*)
                    FROM goals g
                    WHERE g.review_id = r.id AND g.deleted_at IS NULL
                ), 0) AS goals_count,
                COALESCE((
                    SELECT COUNT(*)
                    FROM goals g
                    WHERE g.review_id = r.id
                      AND g.deleted_at IS NULL
                      AND g.score IS NOT NULL
                ), 0) AS scored_goals_count,
                COALESCE((
                    SELECT COUNT(*)
                    FROM competency_scores cs
                    WHERE cs.review_id = r.id AND cs.score IS NOT NULL
                ), 0) AS competency_scores_count
            FROM users u
            LEFT JOIN reviews r ON r.employee_id = u.id
                AND r.deleted_at IS NULL
                AND ($2::int IS NULL OR r.review_year = $2)
            WHERE u.manager_id = $1
              AND u.deleted_at IS NULL
              AND u.is_active = true
            ORDER BY u.last_name ASC, u.first_name ASC
        """
        rows = await self.conn.fetch(query, manager_id, review_year)
        return [dict(row) for row in rows]

    def calculate_scoring_status(
        self,
        goals_count: int,
        scored_goals_count: int,
        competency_scores_count: int,
        total_competencies: int = COMPETENCIES_PER_LEVEL,
    ) -> str:
        """Calculate the scoring status for a team member.

        Args:
            goals_count: Total number of goals
            scored_goals_count: Number of goals with scores
            competency_scores_count: Number of competencies with scores
            total_competencies: Total competencies expected (default 6)

        Returns:
            Status string: 'NOT_STARTED', 'IN_PROGRESS', or 'COMPLETE'
        """
        # Check if nothing has been scored
        if scored_goals_count == 0 and competency_scores_count == 0:
            return 'NOT_STARTED'

        # Check if everything is complete
        goals_complete = (goals_count == 0) or (scored_goals_count >= goals_count)
        competencies_complete = competency_scores_count >= total_competencies

        if goals_complete and competencies_complete:
            return 'COMPLETE'

        # Otherwise, in progress
        return 'IN_PROGRESS'

    async def get_team_members_with_status(
        self, manager_id: UUID, review_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get team members with calculated scoring status.

        Args:
            manager_id: The manager's user UUID
            review_year: Optional filter for specific review year

        Returns:
            List of team member records with scoring_status field
        """
        members = await self.get_team_members_by_manager_id(manager_id, review_year)

        for member in members:
            member['scoring_status'] = self.calculate_scoring_status(
                goals_count=member.get('goals_count', 0),
                scored_goals_count=member.get('scored_goals_count', 0),
                competency_scores_count=member.get('competency_scores_count', 0),
            )

        return members

    async def get_team_members_with_grid_data(
        self, manager_id: UUID, review_year: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get team members with their 9-grid position data.

        Args:
            manager_id: The manager's user UUID
            review_year: Optional filter for specific review year

        Returns:
            List of team member records with WHAT/HOW scores and grid positions
        """
        query = """
            SELECT
                u.id,
                u.email,
                u.first_name,
                u.last_name,
                r.id AS review_id,
                r.status AS review_status,
                r.what_score,
                r.how_score,
                r.grid_position_what,
                r.grid_position_how,
                COALESCE(r.what_veto_active, false) AS what_veto_active,
                COALESCE(r.how_veto_active, false) AS how_veto_active
            FROM users u
            LEFT JOIN reviews r ON r.employee_id = u.id
                AND r.deleted_at IS NULL
                AND ($2::int IS NULL OR r.review_year = $2)
            WHERE u.manager_id = $1
              AND u.deleted_at IS NULL
              AND u.is_active = true
            ORDER BY u.last_name ASC, u.first_name ASC
        """
        rows = await self.conn.fetch(query, manager_id, review_year)
        return [dict(row) for row in rows]
