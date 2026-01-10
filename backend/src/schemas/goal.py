# TSS PPM v3.0 - Goal Schemas
"""Pydantic schemas for goal validation."""

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class GoalType(str, Enum):
    """Goal types with their scoring implications."""

    STANDARD = 'STANDARD'
    KAR = 'KAR'  # Key Area of Responsibility - VETO potential
    SCF = 'SCF'  # Strategic Critical Focus - VETO if score=1


class GoalCreate(BaseModel):
    """Schema for creating a new goal."""

    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    goal_type: GoalType = GoalType.STANDARD
    weight: int = Field(..., ge=5, le=100)

    @field_validator('title')
    @classmethod
    def title_not_whitespace(cls, v: str) -> str:
        """Ensure title is not whitespace only."""
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v

    @field_validator('weight')
    @classmethod
    def weight_multiple_of_5(cls, v: int) -> int:
        """Ensure weight is a multiple of 5."""
        if v % 5 != 0:
            raise ValueError('Weight must be a multiple of 5')
        return v


class GoalUpdate(BaseModel):
    """Schema for updating an existing goal."""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    goal_type: Optional[GoalType] = None
    weight: Optional[int] = Field(None, ge=5, le=100)

    @field_validator('title')
    @classmethod
    def title_not_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not whitespace only when provided."""
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty or whitespace only')
        return v

    @field_validator('weight')
    @classmethod
    def weight_multiple_of_5(cls, v: Optional[int]) -> Optional[int]:
        """Ensure weight is a multiple of 5 when provided."""
        if v is not None and v % 5 != 0:
            raise ValueError('Weight must be a multiple of 5')
        return v


class GoalResponse(BaseModel):
    """Schema for goal API responses."""

    id: UUID
    review_id: UUID
    title: str
    description: Optional[str] = None
    goal_type: GoalType
    weight: int
    score: Optional[int] = Field(None, ge=1, le=3)
    display_order: int

    model_config = {'from_attributes': True}
