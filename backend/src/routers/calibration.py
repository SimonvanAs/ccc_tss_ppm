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
