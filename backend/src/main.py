# TSS PPM v3.0 - FastAPI Application Entry Point
"""Main application module with lifespan management."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.config import settings
from src.database import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup: connect to database
    await db.connect()
    yield
    # Shutdown: disconnect from database
    await db.disconnect()


app = FastAPI(
    title='TSS PPM API',
    description='Performance Portfolio Management API',
    version='3.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Static files for uploaded content (logos, etc.)
# Use /app/static in Docker, or local ./static for development
static_dir = Path(os.environ.get('STATIC_FILES_DIR', '/app/static'))
if not static_dir.exists():
    try:
        static_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Fall back to local directory if Docker path not available
        static_dir = Path(__file__).parent.parent / 'static'
        static_dir.mkdir(parents=True, exist_ok=True)
app.mount('/static', StaticFiles(directory=str(static_dir)), name='static')


@app.get('/health')
async def health_check():
    """Health check endpoint for container orchestration."""
    return {'status': 'healthy'}


@app.get('/ready')
async def readiness_check():
    """Readiness check - verifies database connectivity."""
    try:
        async with db.connection() as conn:
            await conn.fetchval('SELECT 1')
        return {'status': 'ready', 'database': 'connected'}
    except Exception as e:
        return {'status': 'not ready', 'database': str(e)}


# Import and include routers
from src.routers import goals, reviews, manager, competencies, voice, calibration, admin, opco, system, audit

app.include_router(goals.router)
app.include_router(reviews.router)
app.include_router(manager.router)
app.include_router(competencies.router)
app.include_router(voice.router)
app.include_router(calibration.router)
app.include_router(admin.router)
app.include_router(opco.router)
app.include_router(system.router)
app.include_router(audit.router)
