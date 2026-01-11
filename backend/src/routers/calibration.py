# TSS PPM v3.0 - Calibration Router
"""API endpoints for calibration session management."""

from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

import asyncpg

from src.auth import CurrentUser, require_hr
from src.database import get_db
from src.repositories.calibration import CalibrationRepository
from src.schemas.calibration import (
    CalibrationSessionCreate,
    CalibrationSessionUpdate,
    CalibrationSessionResponse,
    CalibrationParticipantCreate,
    CalibrationParticipantResponse,
    CalibrationNoteCreate,
    CalibrationNoteResponse,
    CalibrationReviewResponse,
    ScoreAdjustmentCreate,
    ScoreAdjustmentResponse,
    AdjustmentHistoryResponse,
)

router = APIRouter(prefix='/api/v1/calibration-sessions', tags=['Calibration'])


def _get_user_opco_id(current_user: CurrentUser, conn: asyncpg.Connection) -> UUID:
    """Get the OpCo ID from the current user.

    For now, we use the opco_id from the JWT claims.
    In production, this might need to query the database.
    """
    # The opco_id should be set in the JWT claims
    # For testing, we'll convert the string to UUID
    if isinstance(current_user.opco_id, UUID):
        return current_user.opco_id
    return UUID(current_user.opco_id) if current_user.opco_id else None


async def _get_user_id(current_user: CurrentUser, conn: asyncpg.Connection) -> Optional[UUID]:
    """Get the user ID from keycloak_id."""
    row = await conn.fetchrow(
        'SELECT id FROM users WHERE keycloak_id = $1',
        current_user.keycloak_id,
    )
    return row['id'] if row else None


# --- Session CRUD Endpoints ---

@router.post('', response_model=CalibrationSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: CalibrationSessionCreate,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> CalibrationSessionResponse:
    """Create a new calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)
    user_id = await _get_user_id(current_user, conn)

    session = await repo.create_session(
        opco_id=opco_id,
        name=session_data.name,
        description=session_data.description,
        review_year=session_data.review_year,
        scope=session_data.scope,
        business_unit_id=session_data.business_unit_id,
        facilitator_id=session_data.facilitator_id,
        created_by=user_id,
    )

    return CalibrationSessionResponse(**session)


@router.get('', response_model=List[CalibrationSessionResponse])
async def list_sessions(
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
    status: Annotated[Optional[str], Query(description='Filter by status')] = None,
    review_year: Annotated[Optional[int], Query(description='Filter by review year')] = None,
) -> List[CalibrationSessionResponse]:
    """List calibration sessions for the current OpCo.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    sessions = await repo.list_sessions(
        opco_id=opco_id,
        status=status,
        review_year=review_year,
    )

    return [CalibrationSessionResponse(**session) for session in sessions]


@router.get('/{session_id}', response_model=CalibrationSessionResponse)
async def get_session(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> CalibrationSessionResponse:
    """Get a calibration session by ID.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    session = await repo.get_session_by_id(session_id, opco_id=opco_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    return CalibrationSessionResponse(**session)


@router.put('/{session_id}', response_model=CalibrationSessionResponse)
async def update_session(
    session_id: UUID,
    session_data: CalibrationSessionUpdate,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> CalibrationSessionResponse:
    """Update a calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    # First check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    session = await repo.update_session(
        session_id=session_id,
        name=session_data.name,
        description=session_data.description,
        facilitator_id=session_data.facilitator_id,
        notes=session_data.notes,
    )

    return CalibrationSessionResponse(**session)


@router.delete('/{session_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> None:
    """Delete a calibration session (only if in PREPARATION status).

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    # Check if session exists
    session = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    # Check if session is in PREPARATION status
    if session['status'] != 'PREPARATION':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Can only delete sessions in PREPARATION status',
        )

    await repo.delete_session(session_id)


# --- Status Transition Endpoints ---

@router.post('/{session_id}/start', response_model=CalibrationSessionResponse)
async def start_session(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> CalibrationSessionResponse:
    """Start a calibration session (transition from PREPARATION to IN_PROGRESS).

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    session = await repo.start_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Session must be in PREPARATION status to start',
        )

    return CalibrationSessionResponse(**session)


@router.post('/{session_id}/complete', response_model=CalibrationSessionResponse)
async def complete_session(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> CalibrationSessionResponse:
    """Complete a calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    session = await repo.complete_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Session must be in IN_PROGRESS or PENDING_APPROVAL status to complete',
        )

    return CalibrationSessionResponse(**session)


# --- Review Management Endpoints ---

@router.get('/{session_id}/reviews', response_model=List[CalibrationReviewResponse])
async def get_session_reviews(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> List[CalibrationReviewResponse]:
    """Get all reviews in a calibration session with scores.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    reviews = await repo.get_session_reviews(session_id)
    return [CalibrationReviewResponse(**review) for review in reviews]


@router.post('/{session_id}/reviews/{review_id}', status_code=status.HTTP_201_CREATED)
async def add_review_to_session(
    session_id: UUID,
    review_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> dict:
    """Add a review to a calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)
    user_id = await _get_user_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    await repo.add_review_to_session(session_id, review_id, user_id)
    return {'status': 'added'}


@router.delete('/{session_id}/reviews/{review_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_review_from_session(
    session_id: UUID,
    review_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> None:
    """Remove a review from a calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    await repo.remove_review_from_session(session_id, review_id)


# --- Participant Management Endpoints ---

@router.get('/{session_id}/participants', response_model=List[CalibrationParticipantResponse])
async def get_session_participants(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> List[CalibrationParticipantResponse]:
    """Get all participants in a calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    participants = await repo.get_session_participants(session_id)
    return [CalibrationParticipantResponse(**p) for p in participants]


@router.post('/{session_id}/participants', response_model=CalibrationParticipantResponse, status_code=status.HTTP_201_CREATED)
async def add_participant(
    session_id: UUID,
    participant_data: CalibrationParticipantCreate,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> CalibrationParticipantResponse:
    """Add a participant to a calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)
    added_by = await _get_user_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    participant = await repo.add_participant(
        session_id=session_id,
        user_id=participant_data.user_id,
        role=participant_data.role,
        added_by=added_by,
    )

    return CalibrationParticipantResponse(**participant)


@router.delete('/{session_id}/participants/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_participant(
    session_id: UUID,
    user_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> None:
    """Remove a participant from a calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    await repo.remove_participant(session_id, user_id)


# --- Notes Endpoints ---

@router.get('/{session_id}/notes', response_model=List[CalibrationNoteResponse])
async def get_session_notes(
    session_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
    review_id: Annotated[Optional[UUID], Query(description='Filter by review')] = None,
) -> List[CalibrationNoteResponse]:
    """Get notes for a calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    notes = await repo.get_session_notes(session_id, review_id=review_id)
    return [CalibrationNoteResponse(**note) for note in notes]


@router.post('/{session_id}/notes', response_model=CalibrationNoteResponse, status_code=status.HTTP_201_CREATED)
async def add_note(
    session_id: UUID,
    note_data: CalibrationNoteCreate,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> CalibrationNoteResponse:
    """Add a note to a calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)
    created_by = await _get_user_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    existing = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    note = await repo.add_note(
        session_id=session_id,
        content=note_data.content,
        created_by=created_by,
        review_id=note_data.review_id,
    )

    return CalibrationNoteResponse(**note)


# --- Score Adjustment Endpoints ---

@router.put('/{session_id}/reviews/{review_id}/scores', response_model=ScoreAdjustmentResponse)
async def adjust_review_scores(
    session_id: UUID,
    review_id: UUID,
    adjustment_data: ScoreAdjustmentCreate,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> ScoreAdjustmentResponse:
    """Adjust review scores during calibration.

    Creates an audit trail entry and updates the review scores.
    Only works for sessions in IN_PROGRESS status.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)
    user_id = await _get_user_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    session = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    # Check session is in IN_PROGRESS status
    if session['status'] != 'IN_PROGRESS':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Score adjustments can only be made on sessions in IN_PROGRESS status',
        )

    # Check if review is in the session
    if not await repo.is_review_in_session(session_id, review_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found in this calibration session',
        )

    # Get current scores for response
    current_scores = await repo.get_review_current_scores(review_id)
    if not current_scores:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found',
        )

    # Perform the adjustment
    adjustment = await repo.adjust_review_scores(
        session_id=session_id,
        review_id=review_id,
        what_score=adjustment_data.what_score,
        how_score=adjustment_data.how_score,
        adjusted_by=user_id,
        rationale=adjustment_data.rationale,
    )

    if not adjustment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to create adjustment',
        )

    return ScoreAdjustmentResponse(
        adjustment_id=adjustment['id'],
        session_id=adjustment['session_id'],
        review_id=adjustment['review_id'],
        adjusted_by=adjustment['adjusted_by'],
        original_what_score=float(adjustment['original_what_score']) if adjustment['original_what_score'] else None,
        original_how_score=float(adjustment['original_how_score']) if adjustment['original_how_score'] else None,
        what_score=float(adjustment['adjusted_what_score']) if adjustment['adjusted_what_score'] else None,
        how_score=float(adjustment['adjusted_how_score']) if adjustment['adjusted_how_score'] else None,
        rationale=adjustment['adjustment_notes'],
        created_at=adjustment['created_at'],
    )


@router.get('/{session_id}/reviews/{review_id}/adjustments', response_model=List[AdjustmentHistoryResponse])
async def get_adjustment_history(
    session_id: UUID,
    review_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_hr)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> List[AdjustmentHistoryResponse]:
    """Get the adjustment history for a review in a calibration session.

    Requires HR role.
    """
    repo = CalibrationRepository(conn)
    opco_id = _get_user_opco_id(current_user, conn)

    # Check if session exists and belongs to OpCo
    session = await repo.get_session_by_id(session_id, opco_id=opco_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Calibration session not found',
        )

    adjustments = await repo.get_review_adjustments(session_id, review_id)

    return [
        AdjustmentHistoryResponse(
            id=adj['id'],
            session_id=adj['session_id'],
            review_id=adj['review_id'],
            adjusted_by=adj['adjusted_by'],
            original_what_score=float(adj['original_what_score']) if adj['original_what_score'] else None,
            original_how_score=float(adj['original_how_score']) if adj['original_how_score'] else None,
            adjusted_what_score=float(adj['adjusted_what_score']) if adj['adjusted_what_score'] else None,
            adjusted_how_score=float(adj['adjusted_how_score']) if adj['adjusted_how_score'] else None,
            adjustment_notes=adj['adjustment_notes'],
            created_at=adj['created_at'],
            adjuster_first_name=adj.get('adjuster_first_name'),
            adjuster_last_name=adj.get('adjuster_last_name'),
        )
        for adj in adjustments
    ]
