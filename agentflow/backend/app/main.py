"""
AgentFlow — FastAPI Application Entry Point
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.connection import init_db, close_db, get_pool
from app.db.migrations import run_migrations  # noqa: E402
from app.services import agent_service, session_service, execution_service

# ── Logging setup ─────────────────────────────────────────────────────────────
setup_logging()
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version} [{settings.app_env}]")

    # Database initialization
    db_ok = await init_db()
    if db_ok:
        try:
            pool = await get_pool()
            await run_migrations(pool)
            logger.info("Database migrations complete.")
        except Exception as exc:
            logger.error(f"Migration error: {exc}")
            db_ok = False

    # Notify services of DB availability
    agent_service.set_db_enabled(db_ok)
    session_service.set_db_enabled(db_ok)
    execution_service.set_db_enabled(db_ok)

    if not db_ok:
        logger.warning(
            "Database not available. Persistence is disabled. "
            "Set DATABASE_URL to enable PostgreSQL."
        )

    # Warm up LangGraph
    try:
        from app.graph.graph import get_graph
        get_graph()
        logger.info("LangGraph graph compiled and ready.")
    except Exception as exc:
        logger.error(f"LangGraph init error: {exc}")

    logger.info(f"{settings.app_name} started. Listening on {settings.host}:{settings.port}")
    yield

    # Shutdown
    await close_db()
    logger.info(f"{settings.app_name} shutdown complete.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production LangGraph Agent API Service",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
from app.api import health, models, tools, agents, sessions, executions, chat  # noqa: E402

app.include_router(health.router)
app.include_router(models.router)
app.include_router(tools.router)
app.include_router(agents.router)
app.include_router(sessions.router)
app.include_router(executions.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {"name": settings.app_name, "version": settings.app_version, "docs": "/docs"}
