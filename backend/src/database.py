# TSS PPM v3.0 - Database Connection
"""Async PostgreSQL connection pool using asyncpg."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg

from src.config import settings


class Database:
    """Manages the asyncpg connection pool."""

    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Create the connection pool."""
        self.pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=5,
            max_size=20,
            command_timeout=60,
        )

    async def disconnect(self) -> None:
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a connection from the pool."""
        if not self.pool:
            raise RuntimeError('Database pool not initialized')
        async with self.pool.acquire() as conn:
            yield conn

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a connection with an active transaction."""
        async with self.connection() as conn:
            async with conn.transaction():
                yield conn


# Global database instance
db = Database()


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """FastAPI dependency for database connections."""
    async with db.connection() as conn:
        yield conn
