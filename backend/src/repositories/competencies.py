# TSS PPM v3.0 - Competencies Repository
"""Database operations for competencies."""

import json
from typing import Any, Dict, List, Optional
from uuid import UUID

import asyncpg


class CompetenciesRepository:
    """Repository for competency database operations."""

    def __init__(self, conn: asyncpg.Connection):
        """Initialize repository with database connection.

        Args:
            conn: Async PostgreSQL connection
        """
        self.conn = conn

    async def get_competencies_by_level(
        self, level: str, opco_id: Optional[UUID] = None, language: str = 'en'
    ) -> List[Dict[str, Any]]:
        """Get all competencies for a TOV level.

        Args:
            level: TOV level (A, B, C, or D)
            opco_id: Optional OpCo ID for OpCo-specific competencies
            language: Language code for titles and indicators

        Returns:
            List of competency records
        """
        # Build dynamic columns based on language
        title_col = f'title_{language}' if language in ('en', 'nl', 'es') else 'title_en'
        indicators_col = (
            f'indicators_{language}'
            if language in ('en', 'nl', 'es')
            else 'indicators_en'
        )

        query = f"""
            SELECT
                id,
                level,
                category,
                subcategory,
                {title_col} AS title_en,
                title_nl,
                title_es,
                {indicators_col} AS indicators_en,
                display_order
            FROM competencies
            WHERE level = $1
              AND (opco_id IS NULL OR opco_id = $2)
            ORDER BY category, display_order
        """
        rows = await self.conn.fetch(query, level, opco_id)

        # Parse JSON string columns to lists
        result = []
        for row in rows:
            record = dict(row)
            # Parse indicators_en if it's a string
            if isinstance(record.get('indicators_en'), str):
                try:
                    record['indicators_en'] = json.loads(record['indicators_en'])
                except (json.JSONDecodeError, TypeError):
                    record['indicators_en'] = None
            result.append(record)

        return result
