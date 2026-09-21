"""
AgentFlow — LangGraph Agent State
TypedDict defining the complete state that flows through the graph.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    # ── Identity ─────────────────────────────────────────────
    request_id: str
    session_id: str
    execution_id: str

    # ── Input ────────────────────────────────────────────────
    user_input: str
    messages: List[Dict[str, str]]  # [{"role": "...", "content": "..."}]
    system_prompt: str

    # ── Provider ─────────────────────────────────────────────
    provider: str
    model: str
    requested_provider: str

    # ── Routing ──────────────────────────────────────────────
    intent: str              # "general" | "tool_request"
    requires_tool: bool

    # ── Tool execution ───────────────────────────────────────
    selected_tool: str
    tool_input: Dict[str, Any]
    tool_result: Dict[str, Any]
    tool_duration_ms: int

    # ── Response ─────────────────────────────────────────────
    response: str
    fallback_used: bool
    fallback_reason: str
    actual_provider: str
    actual_model: str

    # ── Observability ────────────────────────────────────────
    execution_status: str    # "running" | "completed" | "failed"
    trace: List[Dict[str, Any]]
    latency_ms: int
    error: str
    error_code: str
