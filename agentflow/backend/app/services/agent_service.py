"""
AgentFlow — Agent Service
Business logic for agent management.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.db import repository as repo

logger = logging.getLogger(__name__)

_DB_ENABLED = False


def set_db_enabled(enabled: bool) -> None:
    global _DB_ENABLED
    _DB_ENABLED = enabled


async def create_agent(
    name: str,
    description: str = "",
    provider: str = "mock",
    model: str = "mock-model",
    system_prompt: str = "",
) -> Dict[str, Any]:
    if not _DB_ENABLED:
        raise RuntimeError("Database not available.")
    return await repo.create_agent(name, description, provider, model, system_prompt)


async def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    if not _DB_ENABLED:
        return None
    return await repo.get_agent(agent_id)


async def list_agents() -> List[Dict[str, Any]]:
    if not _DB_ENABLED:
        return []
    return await repo.list_agents()


async def update_agent(agent_id: str, **kwargs) -> Optional[Dict[str, Any]]:
    if not _DB_ENABLED:
        raise RuntimeError("Database not available.")
    return await repo.update_agent(agent_id, **kwargs)
