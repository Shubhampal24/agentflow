"""
AgentFlow — Database Connection
Manages psycopg3 async connection pool to PostgreSQL (Supabase).
Uses psycopg[binary] which ships pre-built wheels for Python 3.14.
"""
from __future__ import annotations

import logging
from typing import Optional

import psycopg
from psycopg_pool import AsyncConnectionPool

from app.core.config import settings

logger = logging.getLogger(__name__)

_pool: Optional[AsyncConnectionPool] = None


async def get_pool() -> AsyncConnectionPool:
    global _pool
    if _pool is None:
        raise RuntimeError("Database pool not initialized. Call init_db() first.")
    return _pool


async def init_db() -> bool:
    """Initialize the async psycopg3 connection pool. Returns True on success."""
    global _pool
    if not settings.database_url:
        logger.warning("DATABASE_URL not configured — database disabled.")
        return False

    # Normalize URL: psycopg3 uses postgresql:// or postgres://
    dsn = settings.database_url
    dsn = dsn.replace("postgresql+asyncpg://", "postgresql://")
    dsn = dsn.replace("postgresql+psycopg://", "postgresql://")

    try:
        _pool = AsyncConnectionPool(
            conninfo=dsn,
            min_size=1,
            max_size=10,
            open=False,
        )
        await _pool.open()
        logger.info("Database pool (psycopg3) initialized.")
        return True
    except Exception as exc:
        logger.error(f"Database connection failed: {exc}")
        _pool = None
        return False


async def close_db() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed.")


async def is_connected() -> bool:
    """Check if database is reachable."""
    if _pool is None:
        return False
    try:
        async with _pool.connection() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False
