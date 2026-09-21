"""
AgentFlow — Agent Service (core execution)
Orchestrates LangGraph execution with full observability.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.security import generate_request_id
from app.graph.graph import run_graph
from app.services import execution_service, session_service

logger = logging.getLogger(__name__)


async def run_chat(
    session_id: str,
    message: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Main entry point: run the LangGraph agent for a chat message.
    1. Validate session
    2. Load history
    3. Prepare graph state
    4. Run graph
    5. Persist execution
    6. Return structured response
    """
    request_id = generate_request_id()
    start_time = time.perf_counter()

    resolved_provider = provider or settings.default_provider
    resolved_model = model or settings.default_model

    logger.info(
        "Agent run started",
        extra={
            "request_id": request_id,
            "session_id": session_id,
            "provider": resolved_provider,
        },
    )

    # Load session history
    history: List[Dict[str, str]] = []
    try:
        msgs = await session_service.get_messages(session_id)
        history = [{"role": m["role"], "content": m["content"]} for m in msgs]
    except Exception:
        pass  # Non-fatal if DB unavailable

    # Add current user message to history for context
    history.append({"role": "user", "content": message})

    # Create execution record
    execution_rec = await execution_service.create_execution(
        session_id=session_id,
        request=message,
        provider=resolved_provider,
        model=resolved_model,
        requested_provider=resolved_provider,
    )
    execution_id = execution_rec["id"] if execution_rec else ""

    # Build initial graph state
    initial_state: Dict[str, Any] = {
        "request_id": request_id,
        "session_id": session_id,
        "execution_id": execution_id,
        "user_input": message,
        "messages": history,
        "provider": resolved_provider,
        "model": resolved_model,
        "requested_provider": resolved_provider,
        "system_prompt": system_prompt or "You are a helpful AI assistant called AgentFlow.",
        "trace": [
            {
                "event": "request_received",
                "detail": f"provider={resolved_provider}",
                "timestamp": _now_iso(),
            },
            {
                "event": "agent_started",
                "detail": f"session_id={session_id}",
                "timestamp": _now_iso(),
            },
        ],
        "execution_status": "running",
        "requires_tool": False,
        "fallback_used": False,
        "fallback_reason": "",
    }

    # Run graph
    try:
        final_state = await run_graph(initial_state)
    except Exception as exc:
        logger.exception(f"Graph execution error: {exc}")
        total_ms = int((time.perf_counter() - start_time) * 1000)
        await execution_service.update_execution(
            execution_id,
            status="failed",
            error_code="AGENT_ERROR",
            latency_ms=total_ms,
        )
        return {
            "success": False,
            "request_id": request_id,
            "session_id": session_id,
            "error": {"code": "AGENT_ERROR", "message": "The agent encountered an error."},
            "execution_id": execution_id,
            "latency_ms": total_ms,
        }

    total_ms = int((time.perf_counter() - start_time) * 1000)

    # Extract results
    response_text = final_state.get("response", "")
    actual_provider = final_state.get("actual_provider", resolved_provider)
    actual_model = final_state.get("actual_model", resolved_model)
    fallback_used = final_state.get("fallback_used", False)
    fallback_reason = final_state.get("fallback_reason", "")
    exec_status = final_state.get("execution_status", "completed")
    trace = final_state.get("trace", [])
    tool_result = final_state.get("tool_result")
    selected_tool = final_state.get("selected_tool", "")
    tool_duration_ms = final_state.get("tool_duration_ms", 0)
    error_code = final_state.get("error_code", "")

    # Persist messages
    try:
        await session_service.add_message(session_id, "user", message)
        if response_text:
            await session_service.add_message(session_id, "assistant", response_text)
    except Exception as exc:
        logger.warning(f"Message persistence failed: {exc}")

    # Persist tool call
    tools_used = []
    if selected_tool and tool_result:
        try:
            await execution_service.save_tool_call(
                execution_id=execution_id,
                tool_name=selected_tool,
                arguments=final_state.get("tool_input", {}),
                result=tool_result.get("result"),
                status="completed" if tool_result.get("success") else "failed",
                duration_ms=tool_duration_ms,
            )
        except Exception as exc:
            logger.warning(f"Tool call persistence failed: {exc}")

        tools_used = [
            {
                "name": selected_tool,
                "status": "completed" if tool_result.get("success") else "failed",
                "duration_ms": tool_duration_ms,
                "result": tool_result.get("result"),
            }
        ]

    # Update execution record
    await execution_service.update_execution(
        execution_id,
        response=response_text,
        provider=actual_provider,
        model=actual_model,
        requested_provider=resolved_provider,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        status=exec_status,
        latency_ms=total_ms,
        error_code=error_code or None,
        trace=trace,
    )

    logger.info(
        "Agent run completed",
        extra={
            "request_id": request_id,
            "status": exec_status,
            "latency_ms": total_ms,
            "provider": actual_provider,
        },
    )

    return {
        "success": exec_status != "failed",
        "request_id": request_id,
        "session_id": session_id,
        "response": response_text,
        "provider": actual_provider,
        "model": actual_model,
        "requested_provider": resolved_provider,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "tools_used": tools_used,
        "execution_id": execution_id,
        "latency_ms": total_ms,
        "status": exec_status,
        "trace": trace,
        "error_code": error_code,
    }


def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
