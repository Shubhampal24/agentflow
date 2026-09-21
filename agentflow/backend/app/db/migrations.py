"""
AgentFlow — Database Migrations
Idempotent CREATE TABLE IF NOT EXISTS scripts using psycopg3.
"""
from __future__ import annotations

import logging
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)

CREATE_AGENTS = """
CREATE TABLE IF NOT EXISTS agents (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT NOT NULL,
    description TEXT DEFAULT '',
    provider    TEXT NOT NULL DEFAULT 'mock',
    model       TEXT NOT NULL DEFAULT 'mock-model',
    system_prompt TEXT DEFAULT '',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

CREATE_SESSIONS = """
CREATE TABLE IF NOT EXISTS sessions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id    UUID REFERENCES agents(id) ON DELETE SET NULL,
    title       TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

CREATE_SESSIONS_IDX = """
CREATE INDEX IF NOT EXISTS idx_sessions_agent_id ON sessions(agent_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);
"""

CREATE_MESSAGES = """
CREATE TABLE IF NOT EXISTS messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

CREATE_MESSAGES_IDX = """
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
"""

CREATE_EXECUTIONS = """
CREATE TABLE IF NOT EXISTS executions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    request             TEXT,
    response            TEXT,
    provider            TEXT,
    model               TEXT,
    requested_provider  TEXT,
    fallback_used       BOOLEAN DEFAULT FALSE,
    fallback_reason     TEXT,
    status              TEXT NOT NULL DEFAULT 'pending',
    latency_ms          INTEGER,
    error_code          TEXT,
    trace               JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

CREATE_EXECUTIONS_IDX = """
CREATE INDEX IF NOT EXISTS idx_executions_session_id ON executions(session_id);
CREATE INDEX IF NOT EXISTS idx_executions_created_at ON executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
"""

CREATE_TOOL_CALLS = """
CREATE TABLE IF NOT EXISTS tool_calls (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id    UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    tool_name       TEXT NOT NULL,
    arguments       JSONB,
    result          JSONB,
    status          TEXT NOT NULL DEFAULT 'pending',
    duration_ms     INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

CREATE_TOOL_CALLS_IDX = """
CREATE INDEX IF NOT EXISTS idx_tool_calls_execution_id ON tool_calls(execution_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_created_at ON tool_calls(created_at);
"""

ALL_MIGRATIONS = [
    ("agents table", CREATE_AGENTS),
    ("sessions table", CREATE_SESSIONS),
    ("sessions indexes", CREATE_SESSIONS_IDX),
    ("messages table", CREATE_MESSAGES),
    ("messages indexes", CREATE_MESSAGES_IDX),
    ("executions table", CREATE_EXECUTIONS),
    ("executions indexes", CREATE_EXECUTIONS_IDX),
    ("tool_calls table", CREATE_TOOL_CALLS),
    ("tool_calls indexes", CREATE_TOOL_CALLS_IDX),
]


async def run_migrations(pool: AsyncConnectionPool) -> None:
    """Run all idempotent migrations."""
    async with pool.connection() as conn:
        for name, sql in ALL_MIGRATIONS:
            try:
                await conn.execute(sql)
                await conn.commit()
                logger.info(f"Migration OK: {name}")
            except Exception as exc:
                await conn.rollback()
                logger.error(f"Migration failed [{name}]: {exc}")
                raise
