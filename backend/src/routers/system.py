# TSS PPM v3.0 - System Configuration Router
"""System configuration and health monitoring endpoints for admin."""

from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

import asyncpg
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.auth import CurrentUser, get_current_user
from src.config import settings
from src.database import get_db
from src.repositories.audit import AuditRepository


router = APIRouter(prefix='/api/v1/admin/system', tags=['Admin - System'])


# ===== Dependencies =====

async def require_admin(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    """Require admin role for access."""
    if 'admin' not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin role required',
        )
    return current_user


# ===== Schemas =====

class ServiceStatus(BaseModel):
    """Status of a single service."""
    name: str
    status: str  # 'healthy', 'unhealthy', 'unknown'
    latency_ms: float | None = None
    message: str | None = None


class SystemHealthResponse(BaseModel):
    """System health check response."""
    overall_status: str
    timestamp: datetime
    services: dict[str, ServiceStatus]


class VoiceConfigResponse(BaseModel):
    """Voice service configuration."""
    voice_service_url: str
    voice_service_enabled: bool
    voice_model: str


class VoiceConfigUpdate(BaseModel):
    """Voice configuration update request."""
    voice_service_url: str | None = None
    voice_service_enabled: bool | None = None
    voice_model: str | None = None


class ReviewPeriod(BaseModel):
    """Review period configuration."""
    id: str | None = None
    year: int
    stage: str
    start_date: str
    end_date: str
    is_open: bool


class ReviewPeriodsUpdate(BaseModel):
    """Review periods update request."""
    periods: list[ReviewPeriod]


class TogglePeriodRequest(BaseModel):
    """Toggle period open/close request."""
    is_open: bool


# ===== Health Check Endpoint =====

@router.get('/health', response_model=SystemHealthResponse)
async def get_system_health(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> SystemHealthResponse:
    """Get system health status for all services."""
    services: dict[str, ServiceStatus] = {}

    # API is always healthy if we reached this point
    services['api'] = ServiceStatus(
        name='API',
        status='healthy',
        message='FastAPI service running',
    )

    # Check database
    try:
        start = datetime.now()
        await conn.fetchval('SELECT 1')
        latency = (datetime.now() - start).total_seconds() * 1000
        services['database'] = ServiceStatus(
            name='Database',
            status='healthy',
            latency_ms=round(latency, 2),
            message='PostgreSQL connection successful',
        )
    except Exception as e:
        services['database'] = ServiceStatus(
            name='Database',
            status='unhealthy',
            message=str(e),
        )

    # Check Keycloak
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            start = datetime.now()
            keycloak_url = getattr(settings, 'keycloak_url', 'http://keycloak:8080')
            response = await client.get(f'{keycloak_url}/health/ready')
            latency = (datetime.now() - start).total_seconds() * 1000
            if response.status_code == 200:
                services['keycloak'] = ServiceStatus(
                    name='Keycloak',
                    status='healthy',
                    latency_ms=round(latency, 2),
                    message='Keycloak is ready',
                )
            else:
                services['keycloak'] = ServiceStatus(
                    name='Keycloak',
                    status='unhealthy',
                    message=f'Status code: {response.status_code}',
                )
    except Exception as e:
        services['keycloak'] = ServiceStatus(
            name='Keycloak',
            status='unknown',
            message=f'Connection failed: {str(e)}',
        )

    # Check Voice service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            start = datetime.now()
            voice_url = getattr(settings, 'voice_service_url', 'http://whisper:8001')
            response = await client.get(f'{voice_url}/health')
            latency = (datetime.now() - start).total_seconds() * 1000
            if response.status_code == 200:
                services['voice'] = ServiceStatus(
                    name='Voice Service',
                    status='healthy',
                    latency_ms=round(latency, 2),
                    message='Whisper service is ready',
                )
            else:
                services['voice'] = ServiceStatus(
                    name='Voice Service',
                    status='unhealthy',
                    message=f'Status code: {response.status_code}',
                )
    except Exception as e:
        services['voice'] = ServiceStatus(
            name='Voice Service',
            status='unknown',
            message=f'Connection failed: {str(e)}',
        )

    # Determine overall status
    statuses = [s.status for s in services.values()]
    if all(s == 'healthy' for s in statuses):
        overall = 'healthy'
    elif any(s == 'unhealthy' for s in statuses):
        overall = 'degraded'
    else:
        overall = 'partial'

    return SystemHealthResponse(
        overall_status=overall,
        timestamp=datetime.now(),
        services=services,
    )


# ===== Voice Configuration Endpoints =====

@router.get('/voice-config', response_model=VoiceConfigResponse)
async def get_voice_config(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> VoiceConfigResponse:
    """Get voice service configuration."""
    row = await conn.fetchrow(
        """
        SELECT voice_service_url, voice_service_enabled, voice_model
        FROM system_config
        WHERE opco_id = $1
        """,
        UUID(current_user.opco_id),
    )

    if row:
        return VoiceConfigResponse(
            voice_service_url=row['voice_service_url'] or 'http://whisper:8001',
            voice_service_enabled=row['voice_service_enabled'] if row['voice_service_enabled'] is not None else True,
            voice_model=row['voice_model'] or 'whisper-small',
        )

    # Return defaults if no config exists
    return VoiceConfigResponse(
        voice_service_url='http://whisper:8001',
        voice_service_enabled=True,
        voice_model='whisper-small',
    )


@router.put('/voice-config', response_model=VoiceConfigResponse)
async def update_voice_config(
    update: VoiceConfigUpdate,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> VoiceConfigResponse:
    """Update voice service configuration."""
    opco_id = UUID(current_user.opco_id)

    # Build update query dynamically
    updates = []
    values = []
    param_idx = 1

    if update.voice_service_url is not None:
        updates.append(f'voice_service_url = ${param_idx}')
        values.append(update.voice_service_url)
        param_idx += 1

    if update.voice_service_enabled is not None:
        updates.append(f'voice_service_enabled = ${param_idx}')
        values.append(update.voice_service_enabled)
        param_idx += 1

    if update.voice_model is not None:
        updates.append(f'voice_model = ${param_idx}')
        values.append(update.voice_model)
        param_idx += 1

    if updates:
        values.append(opco_id)
        await conn.execute(
            f"""
            INSERT INTO system_config (opco_id, {', '.join(f.split(' = ')[0] for f in updates)})
            VALUES (${param_idx}, {', '.join(f'${i+1}' for i in range(len(values)-1))})
            ON CONFLICT (opco_id) DO UPDATE SET
            {', '.join(updates)},
            updated_at = NOW()
            """,
            *values,
        )

    # Log audit action
    audit = AuditRepository(conn)
    await audit.log_action(
        action='update_voice_config',
        entity_type='system_config',
        entity_id=opco_id,
        user_id=UUID(current_user.keycloak_id),
        opco_id=opco_id,
        changes={'updates': update.model_dump(exclude_none=True)},
    )

    # Return updated config
    return await get_voice_config(current_user, conn)


# ===== Review Periods Endpoints =====

@router.get('/review-periods', response_model=list[ReviewPeriod])
async def get_review_periods(
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> list[ReviewPeriod]:
    """Get review period configuration."""
    rows = await conn.fetch(
        """
        SELECT id, year, stage, start_date::text, end_date::text, is_open
        FROM review_periods
        WHERE opco_id = $1
        ORDER BY year DESC,
            CASE stage
                WHEN 'GOAL_SETTING' THEN 1
                WHEN 'MID_YEAR_REVIEW' THEN 2
                WHEN 'END_YEAR_REVIEW' THEN 3
            END
        """,
        UUID(current_user.opco_id),
    )

    return [
        ReviewPeriod(
            id=str(row['id']),
            year=row['year'],
            stage=row['stage'],
            start_date=row['start_date'],
            end_date=row['end_date'],
            is_open=row['is_open'],
        )
        for row in rows
    ]


@router.put('/review-periods', response_model=list[ReviewPeriod])
async def update_review_periods(
    update: ReviewPeriodsUpdate,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> list[ReviewPeriod]:
    """Update review period configuration."""
    opco_id = UUID(current_user.opco_id)

    for period in update.periods:
        if period.id:
            # Update existing period
            await conn.execute(
                """
                UPDATE review_periods
                SET start_date = $1, end_date = $2, is_open = $3, updated_at = NOW()
                WHERE id = $4 AND opco_id = $5
                """,
                period.start_date,
                period.end_date,
                period.is_open,
                UUID(period.id),
                opco_id,
            )
        else:
            # Insert new period
            await conn.execute(
                """
                INSERT INTO review_periods (opco_id, year, stage, start_date, end_date, is_open)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (opco_id, year, stage) DO UPDATE SET
                start_date = EXCLUDED.start_date,
                end_date = EXCLUDED.end_date,
                is_open = EXCLUDED.is_open,
                updated_at = NOW()
                """,
                opco_id,
                period.year,
                period.stage,
                period.start_date,
                period.end_date,
                period.is_open,
            )

    # Log audit action
    audit = AuditRepository(conn)
    await audit.log_action(
        action='update_review_periods',
        entity_type='review_periods',
        entity_id=opco_id,
        user_id=UUID(current_user.keycloak_id),
        opco_id=opco_id,
        changes={'periods': [p.model_dump() for p in update.periods]},
    )

    return await get_review_periods(current_user, conn)


@router.post('/review-periods/{period_id}/toggle', response_model=ReviewPeriod)
async def toggle_review_period(
    period_id: str,
    request: TogglePeriodRequest,
    current_user: Annotated[CurrentUser, Depends(require_admin)],
    conn: Annotated[asyncpg.Connection, Depends(get_db)],
) -> ReviewPeriod:
    """Toggle a review period open/closed status."""
    opco_id = UUID(current_user.opco_id)

    await conn.execute(
        """
        UPDATE review_periods
        SET is_open = $1, updated_at = NOW()
        WHERE id = $2 AND opco_id = $3
        """,
        request.is_open,
        UUID(period_id),
        opco_id,
    )

    row = await conn.fetchrow(
        """
        SELECT id, year, stage, start_date::text, end_date::text, is_open
        FROM review_periods
        WHERE id = $1 AND opco_id = $2
        """,
        UUID(period_id),
        opco_id,
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review period not found',
        )

    # Log audit action
    audit = AuditRepository(conn)
    await audit.log_action(
        action='toggle_review_period',
        entity_type='review_periods',
        entity_id=UUID(period_id),
        user_id=UUID(current_user.keycloak_id),
        opco_id=opco_id,
        changes={'is_open': request.is_open, 'stage': row['stage'], 'year': row['year']},
    )

    return ReviewPeriod(
        id=str(row['id']),
        year=row['year'],
        stage=row['stage'],
        start_date=row['start_date'],
        end_date=row['end_date'],
        is_open=row['is_open'],
    )
