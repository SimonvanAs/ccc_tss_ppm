# TSS PPM v3.0 - OpCo Router
"""API endpoints for OpCo settings and business units management."""

import os
from pathlib import Path
from typing import Annotated, List, Optional
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from src.auth import CurrentUser, require_admin
from src.database import get_db
from src.repositories.audit import AuditRepository

router = APIRouter(prefix='/api/v1/admin', tags=['OpCo Admin'])


# ============================================================================
# Pydantic Models
# ============================================================================

class ReviewCycleConfig(BaseModel):
    """Review cycle date configuration."""
    goal_setting_start: Optional[str] = None
    goal_setting_end: Optional[str] = None
    mid_year_start: Optional[str] = None
    mid_year_end: Optional[str] = None
    end_year_start: Optional[str] = None
    end_year_end: Optional[str] = None


class OpCoSettings(BaseModel):
    """OpCo settings model."""
    review_cycle: Optional[ReviewCycleConfig] = None


class OpCoResponse(BaseModel):
    """Response model for OpCo settings."""
    id: str
    name: str
    code: str
    logo_url: Optional[str] = None
    default_language: str
    settings: dict


class OpCoUpdateRequest(BaseModel):
    """Request model for updating OpCo settings."""
    name: Optional[str] = None
    default_language: Optional[str] = None
    settings: Optional[dict] = None


class LogoUploadResponse(BaseModel):
    """Response model for logo upload."""
    logo_url: str
    message: str


class BusinessUnitResponse(BaseModel):
    """Response model for business unit."""
    id: str
    opco_id: str
    name: str
    code: str
    parent_id: Optional[str] = None


class BusinessUnitCreateRequest(BaseModel):
    """Request model for creating a business unit."""
    name: str
    code: str
    parent_id: Optional[str] = None


class BusinessUnitUpdateRequest(BaseModel):
    """Request model for updating a business unit."""
    name: Optional[str] = None
    code: Optional[str] = None
    parent_id: Optional[str] = None


# ============================================================================
# Helper Functions
# ============================================================================

def row_to_opco_response(row: dict) -> OpCoResponse:
    """Convert database row to OpCo response."""
    return OpCoResponse(
        id=str(row['id']),
        name=row['name'],
        code=row['code'],
        logo_url=row.get('logo_url'),
        default_language=row.get('default_language', 'en'),
        settings=row.get('settings') or {},
    )


def row_to_business_unit_response(row: dict) -> BusinessUnitResponse:
    """Convert database row to business unit response."""
    return BusinessUnitResponse(
        id=str(row['id']),
        opco_id=str(row['opco_id']),
        name=row['name'],
        code=row['code'],
        parent_id=str(row['parent_id']) if row.get('parent_id') else None,
    )


async def log_admin_action(
    conn: asyncpg.Connection,
    action: str,
    entity_type: str,
    entity_id: UUID,
    admin_user: CurrentUser,
    changes: dict = None,
) -> None:
    """Log an admin action to the audit log."""
    try:
        audit_repo = AuditRepository(conn)
        await audit_repo.log_action(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=UUID(admin_user.keycloak_id) if len(admin_user.keycloak_id) == 36 else None,
            opco_id=UUID(admin_user.opco_id) if admin_user.opco_id and len(admin_user.opco_id) == 36 else None,
            changes=changes or {},
        )
    except Exception:
        # Don't fail the operation if audit logging fails
        pass


# ============================================================================
# OpCo Settings Endpoints
# ============================================================================

async def resolve_opco_id(opco_id_or_code: str, conn: asyncpg.Connection) -> UUID:
    """Resolve an opco_id which may be a UUID or a code to a UUID.

    Args:
        opco_id_or_code: Either a UUID string or an OpCo code
        conn: Database connection

    Returns:
        The OpCo UUID

    Raises:
        HTTPException: If OpCo not found
    """
    # Try to parse as UUID first
    try:
        return UUID(opco_id_or_code)
    except (ValueError, AttributeError):
        pass

    # If not a valid UUID, look up by code
    row = await conn.fetchrow(
        'SELECT id FROM opcos WHERE UPPER(code) = UPPER($1) AND deleted_at IS NULL',
        opco_id_or_code,
    )
    if not row:
        raise HTTPException(status_code=404, detail=f'OpCo not found: {opco_id_or_code}')
    return row['id']


@router.get('/opco/settings', response_model=OpCoResponse)
async def get_opco_settings(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> OpCoResponse:
    """Get current OpCo settings.

    Args:
        current_user: The authenticated admin user
        conn: Database connection

    Returns:
        OpCo settings including review cycle configuration
    """
    opco_id = await resolve_opco_id(current_user.opco_id, conn)
    row = await conn.fetchrow(
        """
        SELECT id, name, code, logo_url, default_language, settings
        FROM opcos
        WHERE id = $1 AND deleted_at IS NULL
        """,
        opco_id,
    )

    if not row:
        raise HTTPException(status_code=404, detail='OpCo not found')

    return row_to_opco_response(dict(row))


@router.put('/opco/settings', response_model=OpCoResponse)
async def update_opco_settings(
    request: OpCoUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> OpCoResponse:
    """Update OpCo settings.

    Args:
        request: The settings to update
        current_user: The authenticated admin user
        conn: Database connection

    Returns:
        Updated OpCo settings
    """
    opco_id = await resolve_opco_id(current_user.opco_id, conn)

    # Build dynamic update query
    updates = []
    values = []
    param_count = 1

    if request.name is not None:
        updates.append(f'name = ${param_count}')
        values.append(request.name)
        param_count += 1

    if request.default_language is not None:
        updates.append(f'default_language = ${param_count}')
        values.append(request.default_language)
        param_count += 1

    if request.settings is not None:
        # Merge with existing settings
        current = await conn.fetchrow(
            'SELECT settings FROM opcos WHERE id = $1',
            opco_id,
        )
        current_settings = dict(current['settings']) if current and current['settings'] else {}
        merged_settings = {**current_settings, **request.settings}

        updates.append(f'settings = ${param_count}::jsonb')
        values.append(merged_settings)
        param_count += 1

    if updates:
        updates.append('updated_at = NOW()')
        values.append(opco_id)

        query = f"""
            UPDATE opcos
            SET {', '.join(updates)}
            WHERE id = ${param_count} AND deleted_at IS NULL
        """
        await conn.execute(query, *values)

    # Log the action
    await log_admin_action(
        conn=conn,
        action='UPDATE_OPCO_SETTINGS',
        entity_type='opco',
        entity_id=opco_id,
        admin_user=current_user,
        changes=request.model_dump(exclude_none=True),
    )

    # Fetch and return updated settings
    row = await conn.fetchrow(
        """
        SELECT id, name, code, logo_url, default_language, settings
        FROM opcos
        WHERE id = $1 AND deleted_at IS NULL
        """,
        opco_id,
    )

    return row_to_opco_response(dict(row))


# Logo storage directory - use /app/static/logos in Docker, fallback for local dev
_static_base = Path(os.environ.get('STATIC_FILES_DIR', '/app/static'))
if not _static_base.exists():
    _static_base = Path(__file__).parent.parent.parent / 'static'
LOGO_STORAGE_DIR = _static_base / 'logos'
ALLOWED_LOGO_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/svg+xml', 'image/webp'}
MAX_LOGO_SIZE = 5 * 1024 * 1024  # 5MB


@router.post('/opco/logo', response_model=LogoUploadResponse)
async def upload_opco_logo(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
    file: UploadFile = File(...),
) -> LogoUploadResponse:
    """Upload a logo for the OpCo.

    Args:
        current_user: The authenticated admin user
        conn: Database connection
        file: The logo file to upload

    Returns:
        The URL to the uploaded logo
    """
    opco_id = await resolve_opco_id(current_user.opco_id, conn)

    # Validate file type
    if file.content_type not in ALLOWED_LOGO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Invalid file type. Allowed types: {", ".join(ALLOWED_LOGO_TYPES)}',
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_LOGO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'File too large. Maximum size is {MAX_LOGO_SIZE // 1024 // 1024}MB',
        )

    # Ensure storage directory exists
    LOGO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    # Generate filename with opco_id to ensure uniqueness
    file_ext = Path(file.filename).suffix if file.filename else '.png'
    if not file_ext:
        # Derive extension from content type
        ext_map = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/gif': '.gif',
            'image/svg+xml': '.svg',
            'image/webp': '.webp',
        }
        file_ext = ext_map.get(file.content_type, '.png')

    filename = f'{opco_id}{file_ext}'
    file_path = LOGO_STORAGE_DIR / filename

    # Delete old logo if exists (different extension)
    for old_file in LOGO_STORAGE_DIR.glob(f'{opco_id}.*'):
        if old_file != file_path:
            old_file.unlink(missing_ok=True)

    # Save the file
    with open(file_path, 'wb') as f:
        f.write(content)

    # Update database with logo URL
    logo_url = f'/static/logos/{filename}'
    await conn.execute(
        """
        UPDATE opcos
        SET logo_url = $1, updated_at = NOW()
        WHERE id = $2 AND deleted_at IS NULL
        """,
        logo_url,
        opco_id,
    )

    # Log the action
    await log_admin_action(
        conn=conn,
        action='UPLOAD_OPCO_LOGO',
        entity_type='opco',
        entity_id=opco_id,
        admin_user=current_user,
        changes={'logo_url': logo_url},
    )

    return LogoUploadResponse(
        logo_url=logo_url,
        message='Logo uploaded successfully',
    )


@router.delete('/opco/logo', status_code=204)
async def delete_opco_logo(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> None:
    """Delete the OpCo logo.

    Args:
        current_user: The authenticated admin user
        conn: Database connection
    """
    opco_id = await resolve_opco_id(current_user.opco_id, conn)

    # Get current logo URL
    row = await conn.fetchrow(
        'SELECT logo_url FROM opcos WHERE id = $1 AND deleted_at IS NULL',
        opco_id,
    )

    if row and row['logo_url']:
        # Delete the file
        file_path = Path('/app') / row['logo_url'].lstrip('/')
        if file_path.exists():
            file_path.unlink(missing_ok=True)

    # Update database
    await conn.execute(
        """
        UPDATE opcos
        SET logo_url = NULL, updated_at = NOW()
        WHERE id = $1 AND deleted_at IS NULL
        """,
        opco_id,
    )

    # Log the action
    await log_admin_action(
        conn=conn,
        action='DELETE_OPCO_LOGO',
        entity_type='opco',
        entity_id=opco_id,
        admin_user=current_user,
    )


# ============================================================================
# Business Units Endpoints
# ============================================================================

@router.get('/business-units', response_model=List[BusinessUnitResponse])
async def list_business_units(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> List[BusinessUnitResponse]:
    """List all business units for the OpCo.

    Args:
        current_user: The authenticated admin user
        conn: Database connection

    Returns:
        List of business units
    """
    rows = await conn.fetch(
        """
        SELECT id, opco_id, name, code, parent_id
        FROM business_units
        WHERE opco_id = $1 AND deleted_at IS NULL
        ORDER BY name
        """,
        await resolve_opco_id(current_user.opco_id, conn),
    )

    return [row_to_business_unit_response(dict(row)) for row in rows]


@router.post('/business-units', response_model=BusinessUnitResponse, status_code=201)
async def create_business_unit(
    request: BusinessUnitCreateRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> BusinessUnitResponse:
    """Create a new business unit.

    Args:
        request: The business unit data
        current_user: The authenticated admin user
        conn: Database connection

    Returns:
        Created business unit
    """
    opco_id = await resolve_opco_id(current_user.opco_id, conn)
    parent_id = UUID(request.parent_id) if request.parent_id else None

    # Verify parent exists if specified
    if parent_id:
        parent = await conn.fetchrow(
            'SELECT id FROM business_units WHERE id = $1 AND opco_id = $2 AND deleted_at IS NULL',
            parent_id,
            opco_id,
        )
        if not parent:
            raise HTTPException(status_code=400, detail='Parent business unit not found')

    row = await conn.fetchrow(
        """
        INSERT INTO business_units (opco_id, name, code, parent_id)
        VALUES ($1, $2, $3, $4)
        RETURNING id, opco_id, name, code, parent_id
        """,
        opco_id,
        request.name,
        request.code,
        parent_id,
    )

    # Log the action
    await log_admin_action(
        conn=conn,
        action='CREATE_BUSINESS_UNIT',
        entity_type='business_unit',
        entity_id=row['id'],
        admin_user=current_user,
        changes={'name': request.name, 'code': request.code},
    )

    return row_to_business_unit_response(dict(row))


@router.put('/business-units/{unit_id}', response_model=BusinessUnitResponse)
async def update_business_unit(
    unit_id: str,
    request: BusinessUnitUpdateRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> BusinessUnitResponse:
    """Update a business unit.

    Args:
        unit_id: The business unit ID
        request: The fields to update
        current_user: The authenticated admin user
        conn: Database connection

    Returns:
        Updated business unit
    """
    opco_id = await resolve_opco_id(current_user.opco_id, conn)
    bu_id = UUID(unit_id)

    # Check unit exists
    existing = await conn.fetchrow(
        'SELECT id FROM business_units WHERE id = $1 AND opco_id = $2 AND deleted_at IS NULL',
        bu_id,
        opco_id,
    )
    if not existing:
        raise HTTPException(status_code=404, detail='Business unit not found')

    # Build dynamic update query
    updates = []
    values = []
    param_count = 1

    if request.name is not None:
        updates.append(f'name = ${param_count}')
        values.append(request.name)
        param_count += 1

    if request.code is not None:
        updates.append(f'code = ${param_count}')
        values.append(request.code)
        param_count += 1

    if request.parent_id is not None:
        parent_id = UUID(request.parent_id) if request.parent_id else None
        updates.append(f'parent_id = ${param_count}')
        values.append(parent_id)
        param_count += 1

    if updates:
        updates.append('updated_at = NOW()')
        values.append(bu_id)
        values.append(opco_id)

        query = f"""
            UPDATE business_units
            SET {', '.join(updates)}
            WHERE id = ${param_count} AND opco_id = ${param_count + 1} AND deleted_at IS NULL
        """
        await conn.execute(query, *values)

    # Log the action
    await log_admin_action(
        conn=conn,
        action='UPDATE_BUSINESS_UNIT',
        entity_type='business_unit',
        entity_id=bu_id,
        admin_user=current_user,
        changes=request.model_dump(exclude_none=True),
    )

    # Fetch and return updated unit
    row = await conn.fetchrow(
        """
        SELECT id, opco_id, name, code, parent_id
        FROM business_units
        WHERE id = $1 AND deleted_at IS NULL
        """,
        bu_id,
    )

    return row_to_business_unit_response(dict(row))


@router.delete('/business-units/{unit_id}', status_code=204)
async def delete_business_unit(
    unit_id: str,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> None:
    """Delete a business unit.

    Args:
        unit_id: The business unit ID
        current_user: The authenticated admin user
        conn: Database connection

    Raises:
        HTTPException: 409 if users are assigned to the unit
    """
    opco_id = await resolve_opco_id(current_user.opco_id, conn)
    bu_id = UUID(unit_id)

    # Check if any users are assigned to this unit
    user_count = await conn.fetchval(
        """
        SELECT COUNT(*) FROM users
        WHERE business_unit_id = $1 AND deleted_at IS NULL
        """,
        bu_id,
    )

    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Cannot delete business unit: {user_count} users assigned to this unit',
        )

    # Soft delete
    await conn.execute(
        """
        UPDATE business_units
        SET deleted_at = NOW()
        WHERE id = $1 AND opco_id = $2 AND deleted_at IS NULL
        """,
        bu_id,
        opco_id,
    )

    # Log the action
    await log_admin_action(
        conn=conn,
        action='DELETE_BUSINESS_UNIT',
        entity_type='business_unit',
        entity_id=bu_id,
        admin_user=current_user,
    )
