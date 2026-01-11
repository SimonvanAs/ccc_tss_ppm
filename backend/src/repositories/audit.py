# TSS PPM v3.0 - Audit Log Repository
"""Database operations for audit logging."""

from typing import Any, Dict, Optional
from uuid import UUID

import asyncpg


class AuditRepository:
    """Repository for audit log database operations."""

    def __init__(self, conn: asyncpg.Connection):
        """Initialize repository with database connection.

        Args:
            conn: Async PostgreSQL connection
        """
        self.conn = conn

    async def log_action(
        self,
        action: str,
        entity_type: str,
        entity_id: UUID,
        user_id: Optional[UUID] = None,
        opco_id: Optional[UUID] = None,
        changes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create an audit log entry.

        Args:
            action: The action performed (e.g., 'SUBMIT_SCORES', 'UPDATE_STATUS')
            entity_type: Type of entity (e.g., 'review', 'goal')
            entity_id: UUID of the affected entity
            user_id: UUID of the user who performed the action
            opco_id: UUID of the operating company
            changes: Dictionary of before/after values

        Returns:
            The created audit log record
        """
        import json

        query = """
            INSERT INTO audit_logs (opco_id, user_id, action, entity_type, entity_id, changes)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, opco_id, user_id, action, entity_type, entity_id, changes, created_at
        """

        changes_json = json.dumps(changes) if changes else None

        row = await self.conn.fetchrow(
            query,
            opco_id,
            user_id,
            action,
            entity_type,
            entity_id,
            changes_json,
        )
        return dict(row) if row else None
