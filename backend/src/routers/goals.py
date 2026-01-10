# TSS PPM v3.0 - Goals Router
"""API endpoints for goal management."""

from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

import asyncpg

from src.auth import CurrentUser, get_current_user
from src.database import get_db
from src.repositories.goals import GoalRepository
from src.schemas.goal import GoalCreate, GoalResponse, GoalUpdate

router = APIRouter(prefix='/api/v1', tags=['Goals'])


class GoalOrderRequest(BaseModel):
    """Request body for reordering goals."""

    goal_ids: List[UUID]


# --- Goal List/Create Endpoints ---


@router.get('/reviews/{review_id}/goals', response_model=List[GoalResponse])
async def get_goals(
    review_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> List[GoalResponse]:
    """Get all goals for a review.

    Args:
        review_id: The review UUID
        current_user: The authenticated user
        conn: Database connection

    Returns:
        List of goals for the review
    """
    repo = GoalRepository(conn)
    goals = await repo.get_goals_by_review(review_id)
    return [GoalResponse(**goal) for goal in goals]


@router.post(
    '/reviews/{review_id}/goals',
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_goal(
    review_id: UUID,
    goal_data: GoalCreate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> GoalResponse:
    """Create a new goal for a review.

    Args:
        review_id: The review UUID
        goal_data: Goal creation data
        current_user: The authenticated user
        conn: Database connection

    Returns:
        The created goal

    Raises:
        HTTPException: If max goals (9) reached
    """
    repo = GoalRepository(conn)

    # Check max goals limit
    count = await repo.get_goal_count(review_id)
    if count >= 9:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Maximum of 9 goals allowed per review',
        )

    goal = await repo.create_goal(review_id, goal_data)
    return GoalResponse(**goal)


# --- Single Goal Endpoints ---


@router.get('/goals/{goal_id}', response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> GoalResponse:
    """Get a single goal by ID.

    Args:
        goal_id: The goal UUID
        current_user: The authenticated user
        conn: Database connection

    Returns:
        The goal

    Raises:
        HTTPException: If goal not found
    """
    repo = GoalRepository(conn)
    goal = await repo.get_goal(goal_id)

    if goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Goal not found',
        )

    return GoalResponse(**goal)


@router.put('/goals/{goal_id}', response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    goal_data: GoalUpdate,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> GoalResponse:
    """Update an existing goal.

    Args:
        goal_id: The goal UUID
        goal_data: Goal update data
        current_user: The authenticated user
        conn: Database connection

    Returns:
        The updated goal

    Raises:
        HTTPException: If goal not found
    """
    repo = GoalRepository(conn)

    # Check goal exists
    existing = await repo.get_goal(goal_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Goal not found',
        )

    # Build updates dict, excluding None values
    updates = goal_data.model_dump(exclude_unset=True)

    goal = await repo.update_goal(goal_id, updates)
    return GoalResponse(**goal)


@router.delete('/goals/{goal_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> None:
    """Delete a goal.

    Args:
        goal_id: The goal UUID
        current_user: The authenticated user
        conn: Database connection

    Raises:
        HTTPException: If goal not found
    """
    repo = GoalRepository(conn)

    # Check goal exists
    existing = await repo.get_goal(goal_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Goal not found',
        )

    await repo.delete_goal(goal_id)


# --- Goal Ordering Endpoint ---


@router.put('/reviews/{review_id}/goals/order')
async def reorder_goals(
    review_id: UUID,
    order_data: GoalOrderRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> dict:
    """Reorder goals for a review.

    Args:
        review_id: The review UUID
        order_data: New goal order
        current_user: The authenticated user
        conn: Database connection

    Returns:
        Success message
    """
    repo = GoalRepository(conn)
    await repo.reorder_goals(review_id, order_data.goal_ids)
    return {'message': 'Goals reordered successfully'}
