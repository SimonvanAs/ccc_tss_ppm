# TSS PPM v3.0 - Competencies Router
"""API endpoints for competency data."""

from typing import Annotated, List

from fastapi import APIRouter, Depends, Query

import asyncpg

from src.auth import CurrentUser, get_current_user
from src.database import get_db
from src.repositories.competencies import CompetenciesRepository
from src.schemas.competency import CompetencyResponse

router = APIRouter(prefix='/api/v1', tags=['Competencies'])


@router.get('/competencies', response_model=List[CompetencyResponse])
async def get_competencies(
    tov_level: Annotated[str, Query(description='TOV level (A, B, C, or D)')],
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
    language: Annotated[str, Query(description='Language code (en, nl, es)')] = 'en',
) -> List[CompetencyResponse]:
    """Get competencies for a specific TOV level.

    Returns the 6 competencies for the specified TOV level (A, B, C, or D),
    organized by category (Dedicated, Entrepreneurial, Innovative).

    Args:
        tov_level: The TOV level to filter by
        current_user: The authenticated user
        conn: Database connection
        language: Language code for indicators (en, nl, es)

    Returns:
        List of competencies for the TOV level
    """
    repo = CompetenciesRepository(conn)

    # Use user's opco_id if available
    opco_id = None
    if current_user.opco_id:
        # Look up UUID from opco code
        opco_row = await conn.fetchrow(
            'SELECT id FROM opcos WHERE code = $1', current_user.opco_id
        )
        if opco_row:
            opco_id = opco_row['id']

    competencies = await repo.get_competencies_by_level(tov_level, opco_id, language)

    return [CompetencyResponse(**c) for c in competencies]
