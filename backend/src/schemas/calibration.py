# TSS PPM v3.0 - Calibration Schemas
"""Pydantic models for calibration session API requests and responses."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CalibrationSessionCreate(BaseModel):
    """Request model for creating a calibration session."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    review_year: int = Field(..., ge=2000, le=2100)
    scope: str = Field(..., pattern='^(BUSINESS_UNIT|COMPANY_WIDE)$')
    business_unit_id: Optional[UUID] = None
    facilitator_id: Optional[UUID] = None


class CalibrationSessionUpdate(BaseModel):
    """Request model for updating a calibration session."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    facilitator_id: Optional[UUID] = None
    notes: Optional[str] = None


class CalibrationSessionResponse(BaseModel):
    """Response model for a calibration session."""

    id: UUID
    opco_id: UUID
    name: str
    description: Optional[str] = None
    review_year: int
    scope: str
    business_unit_id: Optional[UUID] = None
    status: str
    facilitator_id: Optional[UUID] = None
    created_by: Optional[UUID] = None
    snapshot_taken_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalibrationSessionListResponse(BaseModel):
    """Response model for list of calibration sessions."""

    sessions: list[CalibrationSessionResponse]


class CalibrationParticipantCreate(BaseModel):
    """Request model for adding a participant."""

    user_id: UUID
    role: str = Field(default='PARTICIPANT', pattern='^(FACILITATOR|PARTICIPANT|OBSERVER)$')


class CalibrationParticipantResponse(BaseModel):
    """Response model for a calibration participant."""

    user_id: UUID
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None


class CalibrationNoteCreate(BaseModel):
    """Request model for adding a note."""

    content: str = Field(..., min_length=1)
    review_id: Optional[UUID] = None


class CalibrationNoteResponse(BaseModel):
    """Response model for a calibration note."""

    id: UUID
    session_id: UUID
    review_id: Optional[UUID] = None
    content: str
    created_by: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime


class CalibrationReviewResponse(BaseModel):
    """Response model for a review in a calibration session."""

    review_id: UUID
    employee_id: UUID
    employee_name: str
    employee_email: Optional[str] = None
    what_score: Optional[float] = None
    how_score: Optional[float] = None
    grid_position_what: Optional[int] = None
    grid_position_how: Optional[int] = None
    what_veto_active: bool = False
    how_veto_active: bool = False
    review_status: Optional[str] = None
    manager_first_name: Optional[str] = None
    manager_last_name: Optional[str] = None
