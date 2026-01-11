# TSS PPM v3.0 - Manager Router
"""API endpoints for manager operations."""

from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query

import asyncpg

from src.auth import CurrentUser, require_manager
from src.database import get_db
from src.repositories.team import TeamRepository
from src.schemas.team import TeamMemberResponse, ScoringStatus

router = APIRouter(prefix='/api/v1/manager', tags=['Manager'])


@router.get('/team', response_model=List[TeamMemberResponse])
async def get_team(
    current_user: Annotated[CurrentUser, Depends(require_manager)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
    review_year: Annotated[Optional[int], Query(description='Filter by review year')] = None,
) -> List[TeamMemberResponse]:
    """Get the current manager's team members with their review status.

    Args:
        current_user: The authenticated manager
        conn: Database connection
        review_year: Optional filter for specific review year

    Returns:
        List of team members with scoring status
    """
    repo = TeamRepository(conn)

    # Use the keycloak_id to find the manager's user ID in the database
    # For now, we query using the keycloak_id directly
    # In production, this would look up the user ID from keycloak_id
    manager_id_row = await conn.fetchrow(
        'SELECT id FROM users WHERE keycloak_id = $1',
        current_user.keycloak_id,
    )

    if manager_id_row is None:
        # Manager not found in database, return empty list
        return []

    manager_id = manager_id_row['id']
    team_members = await repo.get_team_members_with_status(manager_id, review_year)

    return [
        TeamMemberResponse(
            id=member['id'],
            email=member['email'],
            first_name=member.get('first_name'),
            last_name=member.get('last_name'),
            function_title=member.get('function_title'),
            tov_level=member.get('tov_level'),
            review_id=member.get('review_id'),
            review_stage=member.get('review_stage'),
            review_status=member.get('review_status'),
            scoring_status=ScoringStatus(member['scoring_status']),
        )
        for member in team_members
    ]
