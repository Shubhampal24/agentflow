"""Health check endpoint."""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter

from app.core.config import settings
from app.db.connection import is_connected
from app.llm.factory import get_all_providers
from app.mcp.server import list_tools

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Returns system health status.
    Provider checks do NOT make LLM calls.
    """
    db_status = await is_connected()

    providers = {}
    for pid, provider in get_all_providers().items():
        providers[pid] = provider.is_available()

    tools_available = []
    try:
        tools_available = [t["name"] for t in list_tools()]
        mcp_status = "ready"
    except Exception:
        mcp_status = "unavailable"

    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.app_env,
        "database": "connected" if db_status else "unavailable",
        "mcp": mcp_status,
        "tools": tools_available,
        "providers": providers,
    }
