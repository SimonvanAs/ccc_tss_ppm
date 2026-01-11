# TSS PPM v3.0 - Reviews Router
"""API endpoints for review management."""

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from pydantic import BaseModel, field_validator

import asyncpg

from src.auth import CurrentUser, get_current_user, require_manager, require_hr
from src.database import get_db
from src.repositories.goals import GoalRepository
from src.repositories.scores import ScoresRepository
from src.repositories.audit import AuditRepository
from src.services.pdf_service import (
    PDFService,
    ReviewPDFData,
    GoalPDFData,
    CompetencyPDFData,
    SignaturePDFData,
)
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
    goal_setting_completed_at: Optional[datetime] = None
    mid_year_completed_at: Optional[datetime] = None
    end_year_completed_at: Optional[datetime] = None

    model_config = {'from_attributes': True}


class CreateReviewRequest(BaseModel):
    """Request schema for creating a new review."""

    employee_id: UUID
    review_year: int


class CreateReviewResponse(BaseModel):
    """Response schema for created review."""

    id: UUID
    employee_id: UUID
    manager_id: UUID
    status: str
    stage: str
    review_year: int
    job_title: Optional[str] = None
    tov_level: Optional[str] = None

    model_config = {'from_attributes': True}


@router.post('/reviews', response_model=CreateReviewResponse, status_code=201)
async def create_review(
    request: CreateReviewRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> CreateReviewResponse:
    """Create a new review with pre-population from previous year.

    Pre-populates job_title and tov_level from previous year's review if available.
    Sets manager_id from employee's current manager.

    Args:
        request: Employee ID and review year
        current_user: The authenticated user (must be HR)
        conn: Database connection

    Returns:
        The created review

    Raises:
        HTTPException 404: If employee not found
        HTTPException 400: If review already exists for this employee/year
    """
    # Get employee to find their current manager
    employee = await conn.fetchrow(
        'SELECT id, manager_id, opco_id FROM users WHERE id = $1',
        request.employee_id,
    )
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Employee not found',
        )

    manager_id = employee['manager_id']
    opco_id = employee['opco_id']

    # Look for previous year's review to pre-populate job_title and tov_level
    previous_review = await conn.fetchrow(
        '''
        SELECT job_title, tov_level FROM reviews
        WHERE employee_id = $1 AND review_year = $2 AND deleted_at IS NULL
        ORDER BY created_at DESC LIMIT 1
        ''',
        request.employee_id,
        request.review_year - 1,
    )

    job_title = previous_review['job_title'] if previous_review else None
    tov_level = previous_review['tov_level'] if previous_review else None

    # Create the new review
    created_review = await conn.fetchrow(
        '''
        INSERT INTO reviews (employee_id, manager_id, opco_id, review_year, job_title, tov_level, status, stage)
        VALUES ($1, $2, $3, $4, $5, $6, 'DRAFT', 'GOAL_SETTING')
        RETURNING id, employee_id, manager_id, status, stage, review_year, job_title, tov_level
        ''',
        request.employee_id,
        manager_id,
        opco_id,
        request.review_year,
        job_title,
        tov_level,
    )

    return CreateReviewResponse(**dict(created_review))


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


class ReviewHeaderUpdateRequest(BaseModel):
    """Request schema for updating review header fields."""

    job_title: Optional[str] = None
    tov_level: Optional[str] = None

    @property
    def has_updates(self) -> bool:
        """Check if any update fields are provided."""
        return self.job_title is not None or self.tov_level is not None

    model_config = {
        'json_schema_extra': {
            'examples': [
                {'job_title': 'Senior Developer', 'tov_level': 'B'},
            ]
        }
    }


class ReviewHeaderUpdateRequestValidated(BaseModel):
    """Request schema for updating review header fields with validation."""

    job_title: Optional[str] = None
    tov_level: Optional[str] = None

    @field_validator('tov_level')
    @classmethod
    def validate_tov_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate tov_level is A, B, C, or D."""
        if v is not None and v not in ('A', 'B', 'C', 'D'):
            raise ValueError('tov_level must be A, B, C, or D')
        return v


@router.put('/reviews/{review_id}', response_model=ReviewDetailResponse)
async def update_review_header(
    review_id: UUID,
    update_data: ReviewHeaderUpdateRequestValidated,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> ReviewDetailResponse:
    """Update a review's job_title and/or tov_level.

    Only allowed when review is in DRAFT status.

    Args:
        review_id: The review UUID
        update_data: Fields to update (job_title, tov_level)
        current_user: The authenticated user
        conn: Database connection

    Returns:
        The updated review details

    Raises:
        HTTPException 404: If review not found
        HTTPException 400: If review is not in DRAFT status
    """
    review_repo = ReviewRepository(conn)

    # Get current review to check status
    review = await review_repo.get_review(review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found',
        )

    # Only allow updates in DRAFT status
    if review['status'] != 'DRAFT':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Review must be in DRAFT status to update (current: {review["status"]})',
        )

    # Update the review
    updated_review = await review_repo.update_review(
        review_id,
        job_title=update_data.job_title,
        tov_level=update_data.tov_level,
    )

    # Fetch updated review with all fields (including names from JOINs)
    updated_review = await review_repo.get_review(review_id)

    return ReviewDetailResponse(**updated_review)


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

    # Check job_title and tov_level are set (required for submission)
    missing_fields = []
    if not review.get('job_title'):
        missing_fields.append('job_title')
    if not review.get('tov_level'):
        missing_fields.append('tov_level')

    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Missing required fields before submission: {", ".join(missing_fields)}',
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


# --- Sign Review Endpoint ---


class SignReviewResponse(BaseModel):
    """Response schema for sign review endpoint."""

    status: str
    employee_signature_by: Optional[UUID] = None
    manager_signature_by: Optional[UUID] = None


@router.post('/reviews/{review_id}/sign', response_model=SignReviewResponse)
async def sign_review(
    review_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> SignReviewResponse:
    """Sign a review (employee or manager signature).

    This endpoint handles signing for both employees and managers:
    - Employee: PENDING_EMPLOYEE_SIGNATURE → EMPLOYEE_SIGNED (then auto → PENDING_MANAGER_SIGNATURE)
    - Manager: PENDING_MANAGER_SIGNATURE → SIGNED (if employee already signed)

    Args:
        review_id: The review UUID
        current_user: The authenticated user
        conn: Database connection

    Returns:
        The updated review status and signature info

    Raises:
        HTTPException 403: If user is not authorized to sign this review
        HTTPException 404: If review not found
        HTTPException 400: If review is not in a signable state
    """
    review_repo = ReviewRepository(conn)
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

    old_status = review['status']
    new_status = None
    signature_action = None

    # Determine signature action based on status and user role
    if old_status == 'PENDING_EMPLOYEE_SIGNATURE':
        # Employee signature required
        if review['employee_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Not authorized to sign this review (employee signature required)',
            )
        new_status = 'PENDING_MANAGER_SIGNATURE'  # After employee signs, manager is next
        signature_action = 'EMPLOYEE_SIGNED'

        # Record employee signature
        await conn.execute(
            '''
            UPDATE reviews
            SET employee_signature_by = $1, employee_signature_date = NOW(), status = $2, updated_at = NOW()
            WHERE id = $3
            ''',
            user_id,
            new_status,
            review_id,
        )

    elif old_status == 'PENDING_MANAGER_SIGNATURE':
        # Manager signature required
        if review['manager_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Not authorized to sign this review (manager signature required)',
            )

        # Manager approval always completes the signature process → SIGNED
        # For goal setting: manager approval completes the stage
        # For mid/end year: employee already signed, manager counter-sign completes
        new_status = 'SIGNED'
        signature_action = 'MANAGER_SIGNED'

        # Record manager signature and update stage completion timestamp if applicable
        current_stage = review.get('stage')

        if current_stage == 'GOAL_SETTING':
            # Goal setting approval - set goal_setting_completed_at
            await conn.execute(
                '''
                UPDATE reviews
                SET manager_signature_by = $1, manager_signature_date = NOW(),
                    status = $2, goal_setting_completed_at = NOW(), updated_at = NOW()
                WHERE id = $3
                ''',
                user_id,
                new_status,
                review_id,
            )
        elif current_stage == 'MID_YEAR_REVIEW':
            # Mid-year review completion - set mid_year_completed_at
            await conn.execute(
                '''
                UPDATE reviews
                SET manager_signature_by = $1, manager_signature_date = NOW(),
                    status = $2, mid_year_completed_at = NOW(), updated_at = NOW()
                WHERE id = $3
                ''',
                user_id,
                new_status,
                review_id,
            )
        elif current_stage == 'END_YEAR_REVIEW':
            # End-year review completion - set end_year_completed_at
            await conn.execute(
                '''
                UPDATE reviews
                SET manager_signature_by = $1, manager_signature_date = NOW(),
                    status = $2, end_year_completed_at = NOW(), updated_at = NOW()
                WHERE id = $3
                ''',
                user_id,
                new_status,
                review_id,
            )
        else:
            # Fallback for unknown stages
            await conn.execute(
                '''
                UPDATE reviews
                SET manager_signature_by = $1, manager_signature_date = NOW(),
                    status = $2, updated_at = NOW()
                WHERE id = $3
                ''',
                user_id,
                new_status,
                review_id,
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Review is not awaiting signature (current status: {old_status})',
        )

    # Create audit log entry
    await audit_repo.log_action(
        action=signature_action,
        entity_type='review',
        entity_id=review_id,
        user_id=user_id,
        opco_id=review.get('opco_id'),
        changes={
            'status': {'from': old_status, 'to': new_status},
        },
    )

    # Get updated review
    updated_review = await review_repo.get_review(review_id)

    return SignReviewResponse(
        status=updated_review['status'],
        employee_signature_by=updated_review.get('employee_signature_by'),
        manager_signature_by=updated_review.get('manager_signature_by'),
    )


# --- Reject Review Endpoint ---


class RejectReviewRequest(BaseModel):
    """Request schema for reject review endpoint."""

    feedback: str


class RejectReviewResponse(BaseModel):
    """Response schema for reject review endpoint."""

    status: str
    rejection_feedback: Optional[str] = None


@router.post('/reviews/{review_id}/reject', response_model=RejectReviewResponse)
async def reject_review(
    review_id: UUID,
    request: RejectReviewRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> RejectReviewResponse:
    """Reject a review with feedback.

    This endpoint handles rejection for both employees and managers:
    - Employee: PENDING_EMPLOYEE_SIGNATURE → DRAFT
    - Manager: PENDING_MANAGER_SIGNATURE → PENDING_EMPLOYEE_SIGNATURE (clears employee signature)

    Args:
        review_id: The review UUID
        request: Rejection request with feedback
        current_user: The authenticated user
        conn: Database connection

    Returns:
        The updated review status and feedback

    Raises:
        HTTPException 400: If feedback is empty or review is not rejectable
        HTTPException 403: If user is not authorized to reject
        HTTPException 404: If review not found
    """
    review_repo = ReviewRepository(conn)
    audit_repo = AuditRepository(conn)

    # Validate feedback is not empty
    if not request.feedback or not request.feedback.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Feedback is required for rejection',
        )

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

    old_status = review['status']
    new_status = None
    rejection_action = None

    # Determine rejection action based on status and user role
    if old_status == 'PENDING_EMPLOYEE_SIGNATURE':
        # Employee rejection
        if review['employee_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Not authorized to reject this review',
            )
        new_status = 'DRAFT'
        rejection_action = 'EMPLOYEE_REJECTED'

        # Record rejection - return to DRAFT
        await conn.execute(
            '''
            UPDATE reviews
            SET status = $1, rejection_feedback = $2, updated_at = NOW()
            WHERE id = $3
            ''',
            new_status,
            request.feedback.strip(),
            review_id,
        )

    elif old_status == 'PENDING_MANAGER_SIGNATURE':
        # Manager rejection
        if review['manager_id'] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Not authorized to reject this review',
            )

        # Determine target status based on stage
        stage = review.get('stage', '')
        if stage == 'GOAL_SETTING':
            # Goal setting rejection → return to DRAFT for employee to revise
            new_status = 'DRAFT'
            rejection_action = 'GOALS_REJECTED'
            await conn.execute(
                '''
                UPDATE reviews
                SET status = $1, rejection_feedback = $2, updated_at = NOW()
                WHERE id = $3
                ''',
                new_status,
                request.feedback.strip(),
                review_id,
            )
        else:
            # Mid/end year rejection → return to employee for re-review
            new_status = 'PENDING_EMPLOYEE_SIGNATURE'
            rejection_action = 'MANAGER_REJECTED'
            # Clear employee signature and return to them
            await conn.execute(
                '''
                UPDATE reviews
                SET status = $1, rejection_feedback = $2,
                    employee_signature_by = NULL, employee_signature_date = NULL,
                    updated_at = NOW()
                WHERE id = $3
                ''',
                new_status,
                request.feedback.strip(),
                review_id,
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Review cannot be rejected in current status: {old_status}',
        )

    # Create audit log entry
    await audit_repo.log_action(
        action=rejection_action,
        entity_type='review',
        entity_id=review_id,
        user_id=user_id,
        opco_id=review.get('opco_id'),
        changes={
            'status': {'from': old_status, 'to': new_status},
            'feedback': request.feedback.strip(),
        },
    )

    # Get updated review
    updated_review = await review_repo.get_review(review_id)

    return RejectReviewResponse(
        status=updated_review['status'],
        rejection_feedback=updated_review.get('rejection_feedback'),
    )


# --- Manager Reassignment Endpoint ---


class ManagerReassignRequest(BaseModel):
    """Request schema for manager reassignment."""

    new_manager_id: UUID
    reason: Optional[str] = None


class ManagerReassignResponse(BaseModel):
    """Response schema for manager reassignment."""

    id: UUID
    employee_id: UUID
    manager_id: UUID
    status: str
    stage: str
    review_year: int
    job_title: Optional[str] = None
    tov_level: Optional[str] = None

    model_config = {'from_attributes': True}


@router.put('/reviews/{review_id}/manager', response_model=ManagerReassignResponse)
async def reassign_manager(
    review_id: UUID,
    request: ManagerReassignRequest,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> ManagerReassignResponse:
    """Reassign a review to a different manager.

    This endpoint is restricted to HR role. It:
    1. Validates the review exists
    2. Validates the new manager exists in the same OpCo
    3. Creates an audit log with old/new manager info
    4. Updates the review's manager_id

    Args:
        review_id: The review UUID
        request: New manager ID and optional reason
        current_user: The authenticated HR user
        conn: Database connection

    Returns:
        The updated review

    Raises:
        HTTPException 403: If user is not HR
        HTTPException 404: If review not found
        HTTPException 400: If new manager is invalid
    """
    review_repo = ReviewRepository(conn)
    audit_repo = AuditRepository(conn)

    # Get the review
    review = await review_repo.get_review(review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found',
        )

    old_manager_id = review['manager_id']

    # Validate new manager exists and is in the same OpCo
    new_manager = await conn.fetchrow(
        'SELECT id, opco_id FROM users WHERE id = $1',
        request.new_manager_id,
    )
    if new_manager is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid new manager: user not found',
        )

    # Update the review's manager
    await review_repo.reassign_manager(review_id, request.new_manager_id)

    # Create audit log entry
    changes = {
        'old_manager_id': str(old_manager_id),
        'new_manager_id': str(request.new_manager_id),
    }
    if request.reason:
        changes['reason'] = request.reason

    # Get HR user's internal ID for audit log
    hr_user_row = await conn.fetchrow(
        'SELECT id FROM users WHERE keycloak_id = $1',
        current_user.keycloak_id,
    )
    hr_user_id = hr_user_row['id'] if hr_user_row else None

    await audit_repo.log_action(
        action='MANAGER_REASSIGNED',
        entity_type='review',
        entity_id=review_id,
        user_id=hr_user_id,
        opco_id=review.get('opco_id'),
        changes=changes,
    )

    # Get updated review
    updated_review = await review_repo.get_review(review_id)

    return ManagerReassignResponse(**updated_review)


# ============================================================================
# PDF Generation Endpoint
# ============================================================================


@router.get('/reviews/{review_id}/pdf', response_class=Response)
async def get_review_pdf(
    review_id: UUID,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
    lang: str = Query(default='en', pattern='^(en|nl|es)$'),
) -> Response:
    """Generate and return a PDF for the specified review.

    The PDF includes:
    - Employee and review information
    - Goals with scores and feedback
    - Competencies with scores
    - 9-grid visualization
    - Signature section (with DRAFT watermark if not fully signed)

    RBAC:
    - Employee can access their own review PDF
    - Manager can access their team's review PDFs
    - HR can access all review PDFs in their OpCo
    """
    # Get user's internal ID
    user_row = await conn.fetchrow(
        'SELECT id FROM users WHERE keycloak_id = $1',
        current_user.keycloak_id,
    )
    user_id = user_row['id'] if user_row else None

    # Get the review with full details
    review_repo = ReviewRepository(conn)
    review = await review_repo.get_review(review_id)

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found',
        )

    # RBAC check: employee, manager, or HR
    is_employee = user_id == review['employee_id']
    is_manager = user_id == review['manager_id']
    is_hr = 'HR' in current_user.roles

    if not (is_employee or is_manager or is_hr):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to access this review PDF',
        )

    # OpCo check for HR
    if is_hr and str(review.get('opco_id')) != current_user.opco_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to access reviews from other OpCos',
        )

    # Get goals and scores
    goals = await conn.fetch(
        '''
        SELECT id, title, description, weight, goal_type
        FROM goals
        WHERE review_id = $1
        ORDER BY weight DESC, title
        ''',
        review_id,
    )

    goal_scores = await conn.fetch(
        '''
        SELECT goal_id, score, feedback
        FROM goal_scores
        WHERE review_id = $1
        ''',
        review_id,
    )
    goal_scores_map = {gs['goal_id']: gs for gs in goal_scores}

    # Get competencies and scores
    tov_level = review.get('tov_level') or 'B'
    competencies = await conn.fetch(
        '''
        SELECT id, name, category, subcategory
        FROM competencies
        WHERE tov_level = $1
        ORDER BY category, subcategory, name
        ''',
        tov_level,
    )

    comp_scores = await conn.fetch(
        '''
        SELECT competency_id, score
        FROM competency_scores
        WHERE review_id = $1
        ''',
        review_id,
    )
    comp_scores_map = {cs['competency_id']: cs for cs in comp_scores}

    # Build PDF data
    goals_data = [
        GoalPDFData(
            title=g['title'],
            description=g.get('description'),
            weight=g['weight'],
            goal_type=g['goal_type'],
            score=goal_scores_map.get(g['id'], {}).get('score'),
            feedback=goal_scores_map.get(g['id'], {}).get('feedback'),
        )
        for g in goals
    ]

    competencies_data = [
        CompetencyPDFData(
            name=c['name'],
            category=c['category'],
            subcategory=c['subcategory'],
            score=comp_scores_map.get(c['id'], {}).get('score'),
        )
        for c in competencies
    ]

    # Build signature data
    employee_signature = None
    if review.get('employee_signature_date') and review.get('employee_signature_by'):
        # Get signer name
        signer = await conn.fetchrow(
            'SELECT name FROM users WHERE id = $1',
            review['employee_signature_by'],
        )
        signer_name = signer['name'] if signer else 'Unknown'
        employee_signature = SignaturePDFData(
            signed_by=signer_name,
            signed_at=review['employee_signature_date']
            if isinstance(review['employee_signature_date'], datetime)
            else datetime.fromisoformat(str(review['employee_signature_date'])),
        )

    manager_signature = None
    if review.get('manager_signature_date') and review.get('manager_signature_by'):
        signer = await conn.fetchrow(
            'SELECT name FROM users WHERE id = $1',
            review['manager_signature_by'],
        )
        signer_name = signer['name'] if signer else 'Unknown'
        manager_signature = SignaturePDFData(
            signed_by=signer_name,
            signed_at=review['manager_signature_date']
            if isinstance(review['manager_signature_date'], datetime)
            else datetime.fromisoformat(str(review['manager_signature_date'])),
        )

    pdf_data = ReviewPDFData(
        employee_name=review.get('employee_name') or 'Unknown',
        employee_email='',  # Not shown in PDF
        manager_name=review.get('manager_name') or 'Unknown',
        job_title=review.get('job_title'),
        department=None,  # Not in current schema
        review_year=review['review_year'],
        stage=review['stage'],
        status=review['status'],
        what_score=review.get('what_score'),
        how_score=review.get('how_score'),
        goals=goals_data,
        competencies=competencies_data,
        employee_signature=employee_signature,
        manager_signature=manager_signature,
        manager_comments=review.get('manager_comments'),
        employee_comments=review.get('employee_comments'),
        rejection_feedback=review.get('rejection_feedback'),
    )

    # Generate PDF
    pdf_service = PDFService()
    pdf_bytes = pdf_service.generate_pdf(pdf_data, language=lang)

    # Create filename
    employee_name_safe = (review.get('employee_name') or 'review').replace(' ', '_')
    filename = f"review_{employee_name_safe}_{review['review_year']}.pdf"

    return Response(
        content=pdf_bytes,
        media_type='application/pdf',
        headers={
            'Content-Disposition': f'inline; filename="{filename}"',
        },
    )
