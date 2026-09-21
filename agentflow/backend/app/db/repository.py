"""
AgentFlow — Database Repository
Raw psycopg3 async queries for all CRUD operations.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from app.db.connection import get_pool

logger = logging.getLogger(__name__)


def _row_to_dict(row, cursor) -> Dict[str, Any]:
    """Convert a psycopg3 Row to dict using cursor description."""
    if row is None or cursor.description is None:
        return {}
    cols = [desc.name for desc in cursor.description]
    d = {}
    for k, v in zip(cols, row):
        # Convert UUID objects to str
        d[k] = str(v) if hasattr(v, 'hex') else v
    return d


def _rows_to_list(rows, cursor) -> List[Dict[str, Any]]:
    if cursor.description is None:
        return []
    cols = [desc.name for desc in cursor.description]
    result = []
    for row in rows:
        d = {}
        for k, v in zip(cols, row):
            d[k] = str(v) if hasattr(v, 'hex') else v
        result.append(d)
    return result


# ── Agents ────────────────────────────────────────────────────────────────────

async def create_agent(
    name: str,
    description: str = "",
    provider: str = "mock",
    model: str = "mock-model",
    system_prompt: str = "",
) -> Dict[str, Any]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO agents (name, description, provider, model, system_prompt)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, name, description, provider, model, system_prompt, created_at, updated_at
                """,
                (name, description, provider, model, system_prompt),
            )
            await conn.commit()
            row = await cur.fetchone()
            return _row_to_dict(row, cur)


async def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM agents WHERE id = %s", (agent_id,))
            row = await cur.fetchone()
            return _row_to_dict(row, cur) if row else None


async def list_agents() -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM agents ORDER BY created_at DESC")
            rows = await cur.fetchall()
            return _rows_to_list(rows, cur)


async def update_agent(agent_id: str, **kwargs) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    allowed = {"name", "description", "provider", "model", "system_prompt"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return await get_agent(agent_id)
    set_parts = [f"{k} = %s" for k in updates]
    set_clause = ", ".join(set_parts)
    values = list(updates.values()) + [agent_id]
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"UPDATE agents SET {set_clause}, updated_at = NOW() WHERE id = %s RETURNING *",
                values,
            )
            await conn.commit()
            row = await cur.fetchone()
            return _row_to_dict(row, cur) if row else None


# ── Sessions ──────────────────────────────────────────────────────────────────

async def create_session(
    agent_id: Optional[str] = None,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO sessions (agent_id, title) VALUES (%s, %s) RETURNING *",
                (agent_id, title),
            )
            await conn.commit()
            row = await cur.fetchone()
            return _row_to_dict(row, cur)


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM sessions WHERE id = %s", (session_id,))
            row = await cur.fetchone()
            return _row_to_dict(row, cur) if row else None


async def list_sessions(limit: int = 50) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC LIMIT %s", (limit,)
            )
            rows = await cur.fetchall()
            return _rows_to_list(rows, cur)


# ── Messages ──────────────────────────────────────────────────────────────────

async def create_message(
    session_id: str, role: str, content: str
) -> Dict[str, Any]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s) RETURNING *",
                (session_id, role, content),
            )
            await conn.commit()
            row = await cur.fetchone()
            return _row_to_dict(row, cur)


async def list_messages(session_id: str) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM messages WHERE session_id = %s ORDER BY created_at ASC",
                (session_id,),
            )
            rows = await cur.fetchall()
            return _rows_to_list(rows, cur)


# ── Executions ────────────────────────────────────────────────────────────────

async def create_execution(
    session_id: str,
    request: str,
    provider: str = "",
    model: str = "",
    requested_provider: str = "",
) -> Dict[str, Any]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO executions
                    (session_id, request, provider, model, requested_provider, status)
                VALUES (%s, %s, %s, %s, %s, 'running')
                RETURNING *
                """,
                (session_id, request, provider, model, requested_provider),
            )
            await conn.commit()
            row = await cur.fetchone()
            return _row_to_dict(row, cur)


async def update_execution(execution_id: str, **kwargs) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    allowed = {
        "response", "provider", "model", "requested_provider",
        "fallback_used", "fallback_reason", "status", "latency_ms",
        "error_code", "trace",
    }
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return None

    # Serialize trace
    if "trace" in updates and isinstance(updates["trace"], (dict, list)):
        updates["trace"] = json.dumps(updates["trace"])

    set_parts = [f"{k} = %s" for k in updates]
    set_clause = ", ".join(set_parts)
    values = list(updates.values()) + [execution_id]

    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"UPDATE executions SET {set_clause} WHERE id = %s RETURNING *",
                values,
            )
            await conn.commit()
            row = await cur.fetchone()
            return _row_to_dict(row, cur) if row else None


async def get_execution(execution_id: str) -> Optional[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM executions WHERE id = %s", (execution_id,))
            row = await cur.fetchone()
            return _row_to_dict(row, cur) if row else None


async def list_executions(limit: int = 50) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM executions ORDER BY created_at DESC LIMIT %s", (limit,)
            )
            rows = await cur.fetchall()
            return _rows_to_list(rows, cur)


async def list_session_executions(session_id: str) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM executions WHERE session_id = %s ORDER BY created_at DESC",
                (session_id,),
            )
            rows = await cur.fetchall()
            return _rows_to_list(rows, cur)


# ── Tool Calls ────────────────────────────────────────────────────────────────

async def create_tool_call(
    execution_id: str,
    tool_name: str,
    arguments: dict,
    result: Optional[dict] = None,
    status: str = "completed",
    duration_ms: Optional[int] = None,
) -> Dict[str, Any]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO tool_calls
                    (execution_id, tool_name, arguments, result, status, duration_ms)
                VALUES (%s, %s, %s::jsonb, %s::jsonb, %s, %s)
                RETURNING *
                """,
                (
                    execution_id,
                    tool_name,
                    json.dumps(arguments),
                    json.dumps(result) if result is not None else None,
                    status,
                    duration_ms,
                ),
            )
            await conn.commit()
            row = await cur.fetchone()
            return _row_to_dict(row, cur)


async def list_tool_calls(execution_id: str) -> List[Dict[str, Any]]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM tool_calls WHERE execution_id = %s ORDER BY created_at ASC",
                (execution_id,),
            )
            rows = await cur.fetchall()
            return _rows_to_list(rows, cur)


# ── Stats ─────────────────────────────────────────────────────────────────────

async def get_execution_stats() -> Dict[str, Any]:
    pool = await get_pool()
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM executions")
            total = (await cur.fetchone())[0] or 0

            await cur.execute("SELECT COUNT(*) FROM executions WHERE status = 'completed'")
            completed = (await cur.fetchone())[0] or 0

            await cur.execute("SELECT COUNT(*) FROM executions WHERE status = 'failed'")
            failed = (await cur.fetchone())[0] or 0

            await cur.execute(
                "SELECT AVG(latency_ms) FROM executions WHERE status = 'completed' AND latency_ms IS NOT NULL"
            )
            avg_row = await cur.fetchone()
            avg_latency = float(avg_row[0]) if avg_row and avg_row[0] else None

            return {
                "total": int(total),
                "completed": int(completed),
                "failed": int(failed),
                "avg_latency_ms": round(avg_latency, 1) if avg_latency else None,
            }
