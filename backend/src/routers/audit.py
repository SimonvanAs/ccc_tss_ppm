# TSS PPM v3.0 - Audit Log Router
"""Admin endpoints for viewing and exporting audit logs."""

import csv
import io
import json
from datetime import datetime
from typing import Annotated, Any, Optional
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.dependencies import get_db, require_admin, CurrentUser


router = APIRouter(prefix='/api/v1/admin/audit-logs', tags=['Admin - Audit Logs'])


# ============================================================================
# Pydantic Models
# ============================================================================

class AuditLogEntry(BaseModel):
    """Single audit log entry."""
    id: UUID
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[UUID] = None
    changes: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Paginated list of audit logs."""
    logs: list[AuditLogEntry]
    total: int
    page: int
    page_size: int


class AuditLogFiltersResponse(BaseModel):
    """Available filter options for audit logs."""
    actions: list[str]
    entity_types: list[str]


# ============================================================================
# Helper Functions
# ============================================================================

def build_audit_query(
    opco_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user_id: Optional[UUID] = None,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
) -> tuple[str, list]:
    """Build the WHERE clause and parameters for audit log queries."""
    conditions = ['al.opco_id = $1']
    params: list = [opco_id]
    param_idx = 2

    if start_date:
        conditions.append(f'al.created_at >= ${param_idx}')
        params.append(start_date)
        param_idx += 1

    if end_date:
        conditions.append(f'al.created_at <= ${param_idx}')
        params.append(end_date)
        param_idx += 1

    if user_id:
        conditions.append(f'al.user_id = ${param_idx}')
        params.append(user_id)
        param_idx += 1

    if action:
        conditions.append(f'al.action = ${param_idx}')
        params.append(action)
        param_idx += 1

    if entity_type:
        conditions.append(f'al.entity_type = ${param_idx}')
        params.append(entity_type)
        param_idx += 1

    return ' AND '.join(conditions), params


# ============================================================================
# Endpoints
# ============================================================================

@router.get('', response_model=AuditLogListResponse)
async def list_audit_logs(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
    page: int = Query(1, ge=1, description='Page number'),
    page_size: int = Query(50, ge=1, le=100, description='Items per page'),
    start_date: Optional[datetime] = Query(None, description='Filter by start date'),
    end_date: Optional[datetime] = Query(None, description='Filter by end date'),
    user_id: Optional[UUID] = Query(None, description='Filter by user ID'),
    action: Optional[str] = Query(None, description='Filter by action type'),
    entity_type: Optional[str] = Query(None, description='Filter by entity type'),
) -> AuditLogListResponse:
    """List audit logs with pagination and filtering.

    Filters:
    - start_date/end_date: Date range filter
    - user_id: Filter by the user who performed the action
    - action: Filter by action type (e.g., UPDATE_ROLES, DEACTIVATE_USER)
    - entity_type: Filter by entity type (e.g., user, opco, business_unit)
    """
    where_clause, params = build_audit_query(
        opco_id=current_user['opco_id'],
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
    )

    # Get total count
    count_query = f"""
        SELECT COUNT(*) as total
        FROM audit_logs al
        WHERE {where_clause}
    """
    count_result = await conn.fetchrow(count_query, *params)
    total = count_result['total'] if count_result else 0

    # Get paginated results
    offset = (page - 1) * page_size
    params.extend([page_size, offset])

    query = f"""
        SELECT
            al.id,
            al.user_id,
            al.action,
            al.entity_type,
            al.entity_id,
            al.changes,
            al.ip_address::text as ip_address,
            al.user_agent,
            al.created_at,
            u.email as user_email,
            u.display_name as user_name
        FROM audit_logs al
        LEFT JOIN users u ON al.user_id = u.id
        WHERE {where_clause}
        ORDER BY al.created_at DESC
        LIMIT ${len(params) - 1} OFFSET ${len(params)}
    """

    rows = await conn.fetch(query, *params)

    logs = []
    for row in rows:
        log_dict = dict(row)
        # Parse JSONB changes if present
        if log_dict.get('changes') and isinstance(log_dict['changes'], str):
            log_dict['changes'] = json.loads(log_dict['changes'])
        logs.append(AuditLogEntry(**log_dict))

    return AuditLogListResponse(
        logs=logs,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get('/export')
async def export_audit_logs(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
    start_date: Optional[datetime] = Query(None, description='Filter by start date'),
    end_date: Optional[datetime] = Query(None, description='Filter by end date'),
    user_id: Optional[UUID] = Query(None, description='Filter by user ID'),
    action: Optional[str] = Query(None, description='Filter by action type'),
    entity_type: Optional[str] = Query(None, description='Filter by entity type'),
) -> StreamingResponse:
    """Export audit logs as CSV file.

    Same filters as list endpoint apply. Returns all matching records (no pagination).
    """
    where_clause, params = build_audit_query(
        opco_id=current_user['opco_id'],
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
    )

    query = f"""
        SELECT
            al.id,
            al.user_id,
            al.action,
            al.entity_type,
            al.entity_id,
            al.changes,
            al.ip_address::text as ip_address,
            al.user_agent,
            al.created_at,
            u.email as user_email,
            u.display_name as user_name
        FROM audit_logs al
        LEFT JOIN users u ON al.user_id = u.id
        WHERE {where_clause}
        ORDER BY al.created_at DESC
    """

    rows = await conn.fetch(query, *params)

    # Build CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'ID',
        'Timestamp',
        'User Email',
        'User Name',
        'Action',
        'Entity Type',
        'Entity ID',
        'Changes',
        'IP Address',
        'User Agent',
    ])

    # Write data rows
    for row in rows:
        changes_str = ''
        if row['changes']:
            changes = row['changes'] if isinstance(row['changes'], dict) else json.loads(row['changes'])
            changes_str = json.dumps(changes)

        writer.writerow([
            str(row['id']),
            row['created_at'].isoformat() if row['created_at'] else '',
            row['user_email'] or '',
            row['user_name'] or '',
            row['action'],
            row['entity_type'],
            str(row['entity_id']) if row['entity_id'] else '',
            changes_str,
            row['ip_address'] or '',
            row['user_agent'] or '',
        ])

    output.seek(0)

    # Generate filename with timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f'audit_logs_{timestamp}.csv'

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'},
    )


@router.get('/filters', response_model=AuditLogFiltersResponse)
async def get_filter_options(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> AuditLogFiltersResponse:
    """Get available filter options for audit logs.

    Returns distinct action types and entity types that exist in the audit log.
    """
    # Get distinct actions
    actions_query = """
        SELECT DISTINCT action
        FROM audit_logs
        WHERE opco_id = $1
        ORDER BY action
    """
    actions_rows = await conn.fetch(actions_query, current_user['opco_id'])
    actions = [row['action'] for row in actions_rows]

    # Get distinct entity types
    entity_types_query = """
        SELECT DISTINCT entity_type
        FROM audit_logs
        WHERE opco_id = $1
        ORDER BY entity_type
    """
    entity_types_rows = await conn.fetch(entity_types_query, current_user['opco_id'])
    entity_types = [row['entity_type'] for row in entity_types_rows]

    return AuditLogFiltersResponse(
        actions=actions,
        entity_types=entity_types,
    )


@router.get('/{log_id}', response_model=AuditLogEntry)
async def get_audit_log(
    log_id: UUID,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> AuditLogEntry:
    """Get a single audit log entry by ID."""
    query = """
        SELECT
            al.id,
            al.user_id,
            al.action,
            al.entity_type,
            al.entity_id,
            al.changes,
            al.ip_address::text as ip_address,
            al.user_agent,
            al.created_at,
            u.email as user_email,
            u.display_name as user_name
        FROM audit_logs al
        LEFT JOIN users u ON al.user_id = u.id
        WHERE al.id = $1 AND al.opco_id = $2
    """

    row = await conn.fetchrow(query, log_id, current_user['opco_id'])

    if not row:
        raise HTTPException(status_code=404, detail='Audit log entry not found')

    log_dict = dict(row)
    if log_dict.get('changes') and isinstance(log_dict['changes'], str):
        log_dict['changes'] = json.loads(log_dict['changes'])

    return AuditLogEntry(**log_dict)
