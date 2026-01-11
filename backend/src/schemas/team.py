# TSS PPM v3.0 - Team Schemas
"""Pydantic schemas for team member data."""

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ScoringStatus(str, Enum):
    """Scoring status values."""

    NOT_STARTED = 'NOT_STARTED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETE = 'COMPLETE'


class ReviewStage(str, Enum):
    """Review stage values."""

    GOAL_SETTING = 'GOAL_SETTING'
    MID_YEAR_REVIEW = 'MID_YEAR_REVIEW'
    END_YEAR_REVIEW = 'END_YEAR_REVIEW'


class ReviewStatus(str, Enum):
    """Review status values."""

    DRAFT = 'DRAFT'
    PENDING_EMPLOYEE_SIGNATURE = 'PENDING_EMPLOYEE_SIGNATURE'
    EMPLOYEE_SIGNED = 'EMPLOYEE_SIGNED'
    PENDING_MANAGER_SIGNATURE = 'PENDING_MANAGER_SIGNATURE'
    MANAGER_SIGNED = 'MANAGER_SIGNED'
    SIGNED = 'SIGNED'
    ARCHIVED = 'ARCHIVED'


class TeamMemberResponse(BaseModel):
    """Schema for team member response."""

    id: UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    function_title: Optional[str] = None
    tov_level: Optional[str] = None
    review_id: Optional[UUID] = None
    review_stage: Optional[str] = None
    review_status: Optional[str] = None
    scoring_status: ScoringStatus

    model_config = ConfigDict(from_attributes=True)
