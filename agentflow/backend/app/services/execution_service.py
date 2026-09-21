"""
AgentFlow — Execution Service
Manages execution lifecycle and persistence.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.db import repository as repo

logger = logging.getLogger(__name__)

_DB_ENABLED = False


def set_db_enabled(enabled: bool) -> None:
    global _DB_ENABLED
    _DB_ENABLED = enabled


async def create_execution(
    session_id: str,
    request: str,
    provider: str = "",
    model: str = "",
    requested_provider: str = "",
) -> Optional[Dict[str, Any]]:
    if not _DB_ENABLED:
        return None
    return await repo.create_execution(session_id, request, provider, model, requested_provider)


async def update_execution(execution_id: str, **kwargs) -> Optional[Dict[str, Any]]:
    if not _DB_ENABLED or not execution_id:
        return None
    return await repo.update_execution(execution_id, **kwargs)


async def save_tool_call(
    execution_id: str,
    tool_name: str,
    arguments: dict,
    result: Optional[dict] = None,
    status: str = "completed",
    duration_ms: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    if not _DB_ENABLED or not execution_id:
        return None
    return await repo.create_tool_call(
        execution_id, tool_name, arguments, result, status, duration_ms
    )


async def get_execution(execution_id: str) -> Optional[Dict[str, Any]]:
    if not _DB_ENABLED:
        return None
    return await repo.get_execution(execution_id)


async def list_executions() -> List[Dict[str, Any]]:
    if not _DB_ENABLED:
        return []
    return await repo.list_executions()


async def list_session_executions(session_id: str) -> List[Dict[str, Any]]:
    if not _DB_ENABLED:
        return []
    return await repo.list_session_executions(session_id)


async def get_stats() -> Dict[str, Any]:
    if not _DB_ENABLED:
        return {"total": 0, "completed": 0, "failed": 0, "avg_latency_ms": None}
    return await repo.get_execution_stats()
