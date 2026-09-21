"""
AgentFlow — Session Service
Business logic for session management.
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


async def create_session(
    agent_id: Optional[str] = None, title: Optional[str] = None
) -> Dict[str, Any]:
    if not _DB_ENABLED:
        raise RuntimeError("Database not available.")
    return await repo.create_session(agent_id, title)


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    if not _DB_ENABLED:
        return None
    return await repo.get_session(session_id)


async def list_sessions() -> List[Dict[str, Any]]:
    if not _DB_ENABLED:
        return []
    return await repo.list_sessions()


async def add_message(session_id: str, role: str, content: str) -> Dict[str, Any]:
    if not _DB_ENABLED:
        return {"session_id": session_id, "role": role, "content": content}
    return await repo.create_message(session_id, role, content)


async def get_messages(session_id: str) -> List[Dict[str, Any]]:
    if not _DB_ENABLED:
        return []
    return await repo.list_messages(session_id)
