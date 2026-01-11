# TSS PPM v3.0 - Reviews Router
"""API endpoints for review management."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

import asyncpg

from src.auth import CurrentUser, get_current_user, require_manager
from src.database import get_db
from src.repositories.goals import GoalRepository
from src.repositories.scores import ScoresRepository
from src.repositories.audit import AuditRepository
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
        """Get a single review by ID with employee and manager names.

        Joins with users table to resolve employee and manager names.
        Returns all header fields including job_title, tov_level, and
        stage completion timestamps.
        """
        query = """
            SELECT
                r.id, r.employee_id, r.manager_id, r.opco_id,
                r.status, r.stage, r.review_year,
                r.what_score, r.how_score,
                r.job_title, r.tov_level,
                r.goal_setting_completed_at,
                r.mid_year_completed_at,
                r.end_year_completed_at,
                r.created_at, r.updated_at,
                CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
                CONCAT(m.first_name, ' ', m.last_name) AS manager_name
            FROM reviews r
            LEFT JOIN users e ON r.employee_id = e.id
            LEFT JOIN users m ON r.manager_id = m.id
            WHERE r.id = $1 AND r.deleted_at IS NULL
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

    async def update_review(
        self,
        review_id: UUID,
        job_title: Optional[str] = None,
        tov_level: Optional[str] = None,
    ) -> Optional[dict]:
        """Update a review's job_title and/or tov_level.

        Only updates provided fields. Returns the updated review.

        Args:
            review_id: The review UUID
            job_title: New job title (optional)
            tov_level: New TOV level A/B/C/D (optional)

        Returns:
            Updated review dict or None if not found
        """
        # Build dynamic SET clause
        set_parts = ['updated_at = NOW()']
        params = []
        param_idx = 1

        if job_title is not None:
            set_parts.append(f'job_title = ${param_idx}')
            params.append(job_title)
            param_idx += 1

        if tov_level is not None:
            set_parts.append(f'tov_level = ${param_idx}')
            params.append(tov_level)
            param_idx += 1

        params.append(review_id)

        query = f"""
            UPDATE reviews
            SET {', '.join(set_parts)}
            WHERE id = ${param_idx} AND deleted_at IS NULL
            RETURNING id, employee_id, manager_id, status, stage, review_year,
                      what_score, how_score, job_title, tov_level
        """
        row = await self.conn.fetchrow(query, *params)
        return dict(row) if row else None

    async def reassign_manager(
        self, review_id: UUID, new_manager_id: UUID
    ) -> Optional[dict]:
        """Reassign a review to a different manager.

        Args:
            review_id: The review UUID
            new_manager_id: The new manager's user UUID

        Returns:
            Updated review dict or None if not found
        """
        query = """
            UPDATE reviews
            SET manager_id = $1, updated_at = NOW()
            WHERE id = $2 AND deleted_at IS NULL
            RETURNING id, employee_id, manager_id, opco_id, status, stage,
                      review_year, what_score, how_score, job_title, tov_level
        """
        row = await self.conn.fetchrow(query, new_manager_id, review_id)
        return dict(row) if row else None


class ReviewDetailResponse(BaseModel):
    """Schema for detailed review API responses including TOV level."""

    id: UUID
    employee_id: UUID
    manager_id: UUID
    status: str
    stage: str
    review_year: int
    tov_level: Optional[str] = None
    job_title: Optional[str] = None
    what_score: Optional[float] = None
    how_score: Optional[float] = None
    employee_name: Optional[str] = None
    manager_name: Optional[str] = None

    model_config = {'from_attributes': True}


@router.get('/reviews/{review_id}', response_model=ReviewDetailResponse)
async def get_review(
    review_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> ReviewDetailResponse:
    """Get a review by ID.

    Args:
        review_id: The review UUID
        current_user: The authenticated user
        conn: Database connection

    Returns:
        The review details

    Raises:
        HTTPException: If review not found
    """
    review_repo = ReviewRepository(conn)
    review = await review_repo.get_review(review_id)

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found',
        )

    return ReviewDetailResponse(**review)


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


# --- Submit Scores Endpoint ---


class SubmitScoresResponse(BaseModel):
    """Response schema for submit scores endpoint."""

    status: str


REQUIRED_COMPETENCY_COUNT = 6


@router.post('/reviews/{review_id}/submit-scores', response_model=SubmitScoresResponse)
async def submit_scores(
    review_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_manager)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> SubmitScoresResponse:
    """Submit scores for a review, transitioning status to PENDING_EMPLOYEE_SIGNATURE.

    This endpoint validates that:
    1. The current user is the manager of the review
    2. The review is in DRAFT status
    3. All goals have scores
    4. All 6 competencies have scores

    On success, transitions status from DRAFT to PENDING_EMPLOYEE_SIGNATURE
    and creates an audit log entry.

    Args:
        review_id: The review UUID
        current_user: The authenticated manager
        conn: Database connection

    Returns:
        The updated review status

    Raises:
        HTTPException 403: If user is not the manager of the review
        HTTPException 404: If review not found
        HTTPException 400: If review not in DRAFT status or scores incomplete
    """
    review_repo = ReviewRepository(conn)
    scores_repo = ScoresRepository(conn)
    audit_repo = AuditRepository(conn)

    # Get user's internal ID from keycloak_id
    user_row = await conn.fetchrow(
        'SELECT id FROM users WHERE keycloak_id = $1',
        current_user.keycloak_id,
    )
    if user_row is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User not found in database',
        )
    user_id = user_row['id']

    # Get the review
    review = await review_repo.get_review(review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found',
        )

    # Check authorization: only the manager of the review can submit
    if review['manager_id'] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to submit scores for this review',
        )

    # Check review is in DRAFT status
    if review['status'] != 'DRAFT':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Review must be in DRAFT status to submit scores (current: {review["status"]})',
        )

    # Validate all goals have scores
    goal_scores = await scores_repo.get_goal_scores(review_id)
    unscored_goals = [g for g in goal_scores if g.get('score') is None]
    if unscored_goals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'All goals must have scores before submitting ({len(unscored_goals)} goal(s) missing scores)',
        )

    # Validate all competencies have scores (6 required)
    competency_scores = await conn.fetch(
        'SELECT score FROM competency_scores WHERE review_id = $1',
        review_id,
    )
    if len(competency_scores) < REQUIRED_COMPETENCY_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'All {REQUIRED_COMPETENCY_COUNT} competencies must have scores before submitting '
            f'({len(competency_scores)} scored)',
        )

    # Update status to PENDING_EMPLOYEE_SIGNATURE
    new_status = 'PENDING_EMPLOYEE_SIGNATURE'
    old_status = review['status']

    updated_review = await review_repo.update_status(review_id, new_status)

    # Create audit log entry
    await audit_repo.log_action(
        action='SUBMIT_SCORES',
        entity_type='review',
        entity_id=review_id,
        user_id=user_id,
        opco_id=review.get('opco_id'),
        changes={
            'status': {'from': old_status, 'to': new_status},
        },
    )

    return SubmitScoresResponse(status=updated_review['status'])
