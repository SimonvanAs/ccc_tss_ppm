# TSS PPM v3.0 - Scores Schemas
"""Pydantic schemas for score data."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GoalScoreResponse(BaseModel):
    """Schema for goal score response."""

    id: UUID
    review_id: UUID
    title: str
    description: Optional[str] = None
    goal_type: str
    weight: int
    score: Optional[int] = None
    feedback: Optional[str] = None
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class CompetencyScoreResponse(BaseModel):
    """Schema for competency score response."""

    id: UUID
    review_id: UUID
    competency_id: UUID
    score: Optional[int] = None
    notes: Optional[str] = None
    category: str
    subcategory: str
    title_en: str
    display_order: int

    model_config = ConfigDict(from_attributes=True)


class AllScoresResponse(BaseModel):
    """Schema for combined scores response."""

    goal_scores: List[GoalScoreResponse]
    competency_scores: List[CompetencyScoreResponse]


class GoalScoreUpdate(BaseModel):
    """Schema for updating a single goal score."""

    goal_id: UUID
    score: int = Field(..., ge=1, le=3)
    feedback: Optional[str] = None


class CompetencyScoreUpdate(BaseModel):
    """Schema for updating a single competency score."""

    competency_id: UUID
    score: int = Field(..., ge=1, le=3)
    notes: Optional[str] = None


class ScoresUpdateRequest(BaseModel):
    """Schema for updating scores request."""

    goal_scores: Optional[List[GoalScoreUpdate]] = None
    competency_scores: Optional[List[CompetencyScoreUpdate]] = None


class ScoresUpdateResponse(BaseModel):
    """Schema for scores update response."""

    message: str
    updated_goals: int
    updated_competencies: int
