# TSS PPM v3.0 - Reviews Router
"""API endpoints for review management."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

import asyncpg

from src.auth import CurrentUser, get_current_user
from src.database import get_db
from src.repositories.goals import GoalRepository
from src.repositories.scores import ScoresRepository
from src.schemas.scores import (
    AllScoresResponse,
    GoalScoreResponse,
    CompetencyScoreResponse,
    ScoresUpdateRequest,
    ScoresUpdateResponse,
)

router = APIRouter(prefix='/api/v1', tags=['Reviews'])


class ReviewResponse(BaseModel):
    """Schema for review API responses."""

    id: UUID
    employee_id: UUID
    manager_id: UUID
    status: str
    stage: str
    review_year: int
    what_score: Optional[float] = None
    how_score: Optional[float] = None

    model_config = {'from_attributes': True}


class ReviewRepository:
    """Repository for review database operations."""

    def __init__(self, conn: asyncpg.Connection):
        self.conn = conn

    async def get_review(self, review_id: UUID) -> Optional[dict]:
        """Get a single review by ID."""
        query = """
            SELECT id, employee_id, manager_id, status, stage, review_year,
                   what_score, how_score
            FROM reviews
            WHERE id = $1 AND deleted_at IS NULL
        """
        row = await self.conn.fetchrow(query, review_id)
        return dict(row) if row else None

    async def update_status(self, review_id: UUID, new_status: str) -> Optional[dict]:
        """Update a review's status."""
        query = """
            UPDATE reviews
            SET status = $1, updated_at = NOW()
            WHERE id = $2 AND deleted_at IS NULL
            RETURNING id, employee_id, manager_id, status, stage, review_year,
                      what_score, how_score
        """
        row = await self.conn.fetchrow(query, new_status, review_id)
        return dict(row) if row else None


@router.post('/reviews/{review_id}/submit', response_model=ReviewResponse)
async def submit_review(
    review_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> ReviewResponse:
    """Submit a review after goal setting is complete.

    Validates that:
    1. Review exists
    2. Review is in DRAFT status
    3. Goal weights total 100%

    On success, transitions status to PENDING_MANAGER_SIGNATURE.

    Args:
        review_id: The review UUID
        current_user: The authenticated user
        conn: Database connection

    Returns:
        The updated review

    Raises:
        HTTPException: If validation fails
    """
    review_repo = ReviewRepository(conn)
    goal_repo = GoalRepository(conn)

    # Check review exists
    review = await review_repo.get_review(review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found',
        )

    # Check review is in DRAFT status
    if review['status'] != 'DRAFT':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Review must be in DRAFT status to submit (current: {review["status"]})',
        )

    # Check weights total 100%
    weight_total = await goal_repo.get_weight_total(review_id)
    if weight_total != 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Goal weights must total 100% (current: {weight_total}%)',
        )

    # Update status to PENDING_MANAGER_SIGNATURE
    updated_review = await review_repo.update_status(
        review_id, 'PENDING_MANAGER_SIGNATURE'
    )

    return ReviewResponse(**updated_review)


# --- Scores Endpoints ---


@router.get('/reviews/{review_id}/scores', response_model=AllScoresResponse)
async def get_scores(
    review_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> AllScoresResponse:
    """Get all scores (goals and competencies) for a review.

    Args:
        review_id: The review UUID
        current_user: The authenticated user
        conn: Database connection

    Returns:
        Combined goal and competency scores
    """
    scores_repo = ScoresRepository(conn)
    scores = await scores_repo.get_all_scores(review_id)

    return AllScoresResponse(
        goal_scores=[GoalScoreResponse(**g) for g in scores['goal_scores']],
        competency_scores=[
            CompetencyScoreResponse(**c) for c in scores['competency_scores']
        ],
    )


@router.put('/reviews/{review_id}/scores', response_model=ScoresUpdateResponse)
async def update_scores(
    review_id: UUID,
    scores_data: ScoresUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> ScoresUpdateResponse:
    """Update scores for a review.

    Allows partial updates - you can update only goals, only competencies, or both.

    Args:
        review_id: The review UUID
        scores_data: Scores to update
        current_user: The authenticated user
        conn: Database connection

    Returns:
        Update confirmation with counts
    """
    scores_repo = ScoresRepository(conn)

    updated_goals = 0
    updated_competencies = 0

    # Update goal scores if provided
    if scores_data.goal_scores:
        goal_updates = [
            {'goal_id': gs.goal_id, 'score': gs.score, 'feedback': gs.feedback}
            for gs in scores_data.goal_scores
        ]
        results = await scores_repo.bulk_upsert_goal_scores(goal_updates)
        updated_goals = len(results)

    # Update competency scores if provided
    if scores_data.competency_scores:
        comp_updates = [
            {'competency_id': cs.competency_id, 'score': cs.score, 'notes': cs.notes}
            for cs in scores_data.competency_scores
        ]
        results = await scores_repo.bulk_upsert_competency_scores(review_id, comp_updates)
        updated_competencies = len(results)

    return ScoresUpdateResponse(
        message='Scores updated successfully',
        updated_goals=updated_goals,
        updated_competencies=updated_competencies,
    )
