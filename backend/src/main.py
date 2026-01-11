# TSS PPM v3.0 - FastAPI Application Entry Point
"""Main application module with lifespan management."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
from src.routers import goals, reviews, manager, competencies, voice, calibration, admin

app.include_router(goals.router)
app.include_router(reviews.router)
app.include_router(manager.router)
app.include_router(competencies.router)
app.include_router(voice.router)
app.include_router(calibration.router)
app.include_router(admin.router)
