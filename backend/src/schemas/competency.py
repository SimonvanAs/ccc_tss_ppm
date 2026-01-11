# TSS PPM v3.0 - Competency Schemas
"""Pydantic schemas for competency data."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CompetencyResponse(BaseModel):
    """Schema for competency response."""

    id: UUID
    level: str
    category: str
    subcategory: str
    title_en: str
    title_nl: Optional[str] = None
    title_es: Optional[str] = None
    indicators_en: Optional[List[str]] = None
    display_order: int

    model_config = ConfigDict(from_attributes=True)
