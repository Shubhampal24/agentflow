"""
AgentFlow — LangGraph Nodes
Each node is a pure function: AgentState → dict (partial state update).
"""
from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.graph.state import AgentState
from app.llm.base import LLMMessage
from app.llm.factory import invoke_with_fallback
from app.mcp.client import mcp_client

logger = logging.getLogger(__name__)

# ── Intent detection ─────────────────────────────────────────────────────────

_TOOL_PATTERNS = [
    # calculator
    (r"calculat|compute|evaluate|solve|math|\d+\s*[\+\-\*×\/÷\%\^]\s*\d+", "calculator"),
    # current_time
    (r"\btime\b|\bclock\b|\bwhat.?time|\bdate.?today|\btoday.?date|\btimezone\b|\bin\s+[A-Z][a-z]+\/", "current_time"),
    # text_stats
    (r"word count|count (the )?(words|sentences|chars)|text stat|how many words|analyze.?text|character count", "text_stats"),
]


def _detect_intent(user_input: str) -> tuple[str, bool, str]:
    """
    Returns (intent, requires_tool, selected_tool).
    Deterministic heuristic routing for the three built-in tools.
    """
    lower = user_input.lower()
    for pattern, tool in _TOOL_PATTERNS:
        if re.search(pattern, lower):
            return "tool_request", True, tool
    return "general", False, ""


def _extract_tool_input(user_input: str, tool_name: str) -> Dict[str, Any]:
    """Extract tool-specific input from user message."""
    if tool_name == "calculator":
        # Try to find a math expression
        match = re.search(r"[\d\.\s\+\-\*\/\%\^\(\)]+", user_input)
        if match:
            expr = match.group(0).strip()
            if expr:
                return {"expression": expr}
        return {"expression": user_input}

    elif tool_name == "current_time":
        # Try to find a timezone
        tz_match = re.search(
            r'\b([A-Z][a-z]+/[A-Z][a-z_]+|UTC|GMT|EST|PST|IST|CST|MST)\b', user_input
        )
        if tz_match:
            return {"timezone": tz_match.group(1)}
        # Look for common city patterns
        city_match = re.search(
            r'\b(Kolkata|London|Tokyo|New_York|Los_Angeles|Chicago|Sydney|Dubai)\b',
            user_input, re.IGNORECASE
        )
        if city_match:
            city = city_match.group(1).replace(" ", "_").title()
            tz_map = {
                "Kolkata": "Asia/Kolkata", "London": "Europe/London",
                "Tokyo": "Asia/Tokyo", "New_York": "America/New_York",
                "Los_Angeles": "America/Los_Angeles", "Chicago": "America/Chicago",
                "Sydney": "Australia/Sydney", "Dubai": "Asia/Dubai",
            }
            return {"timezone": tz_map.get(city, "UTC")}
        return {"timezone": "UTC"}

    elif tool_name == "text_stats":
        # Try to extract quoted text or text after "text:"
        quoted = re.search(r'"([^"]+)"', user_input) or re.search(r"'([^']+)'", user_input)
        if quoted:
            return {"text": quoted.group(1)}
        colon = re.search(r'(?:text|analyze|stats?)\s*[:]\s*(.+)', user_input, re.IGNORECASE)
        if colon:
            return {"text": colon.group(1).strip()}
        return {"text": user_input}

    return {}


def _add_trace(state: AgentState, event: str, detail: str = "") -> List[Dict]:
    trace = list(state.get("trace", []) or [])
    trace.append({
        "event": event,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return trace


# ── Nodes ─────────────────────────────────────────────────────────────────────


def analyze_request(state: AgentState) -> Dict:
    """Analyze the user request and determine intent."""
    user_input = state.get("user_input", "")
    intent, requires_tool, selected_tool = _detect_intent(user_input)

    logger.info(
        f"analyze_request: intent={intent} requires_tool={requires_tool} tool={selected_tool}",
        extra={"request_id": state.get("request_id")},
    )

    trace = _add_trace(
        state, "request_analyzed",
        f"intent={intent} tool={selected_tool or 'none'}"
    )

    result = {
        "intent": intent,
        "requires_tool": requires_tool,
        "trace": trace,
    }
    if selected_tool:
        result["selected_tool"] = selected_tool
    return result


def select_tool(state: AgentState) -> Dict:
    """Prepare tool input based on the selected tool and user input."""
    tool_name = state.get("selected_tool", "")
    user_input = state.get("user_input", "")
    tool_input = _extract_tool_input(user_input, tool_name)

    trace = _add_trace(
        state, "tool_selected",
        f"tool={tool_name} input_keys={list(tool_input.keys())}"
    )
    return {"tool_input": tool_input, "trace": trace}


def execute_mcp_tool(state: AgentState) -> Dict:
    """Execute the selected tool via the MCP client."""
    tool_name = state.get("selected_tool", "")
    tool_input = state.get("tool_input", {})

    trace = _add_trace(state, "mcp_tool_started", f"tool={tool_name}")

    result = mcp_client.call_tool(tool_name, tool_input)

    if result.success:
        trace = _add_trace(
            {"trace": trace}, "mcp_tool_completed",
            f"tool={tool_name} duration={result.duration_ms}ms"
        )
        return {
            "tool_result": result.to_dict(),
            "tool_duration_ms": result.duration_ms,
            "trace": trace,
        }
    else:
        trace = _add_trace(
            {"trace": trace}, "mcp_tool_failed",
            f"tool={tool_name} error={result.error}"
        )
        return {
            "tool_result": result.to_dict(),
            "tool_duration_ms": result.duration_ms,
            "trace": trace,
            "error": result.error,
            "error_code": "MCP_TOOL_ERROR",
        }


async def direct_response(state: AgentState) -> Dict:
    """Generate a direct LLM response (no tool needed)."""
    provider = state.get("provider", "mock")
    model = state.get("model") or None
    system_prompt = state.get("system_prompt", "You are a helpful AI assistant.")

    messages_raw = state.get("messages", [])
    messages = [LLMMessage(role=m["role"], content=m["content"]) for m in messages_raw]
    if not messages:
        messages = [LLMMessage(role="user", content=state.get("user_input", ""))]

    trace = _add_trace(state, "llm_started", f"provider={provider}")

    start = time.perf_counter()
    llm_response = await invoke_with_fallback(
        messages=messages,
        requested_provider=provider,
        model=model,
        system_prompt=system_prompt,
    )
    latency_ms = int((time.perf_counter() - start) * 1000)

    if llm_response.success:
        trace = _add_trace(
            {"trace": trace}, "llm_completed",
            f"provider={llm_response.provider} model={llm_response.model}"
        )
        trace = _add_trace(
            {"trace": trace}, "execution_completed", "status=completed"
        )
        return {
            "response": llm_response.content,
            "actual_provider": llm_response.provider,
            "actual_model": llm_response.model,
            "fallback_used": llm_response.fallback_used,
            "fallback_reason": llm_response.fallback_reason,
            "execution_status": "completed",
            "latency_ms": latency_ms,
            "trace": trace,
        }
    else:
        trace = _add_trace(
            {"trace": trace}, "execution_failed",
            f"error={llm_response.error_code}"
        )
        return {
            "response": "",
            "actual_provider": llm_response.provider,
            "actual_model": llm_response.model,
            "execution_status": "failed",
            "error": llm_response.error_message,
            "error_code": llm_response.error_code,
            "latency_ms": latency_ms,
            "trace": trace,
        }


async def final_response(state: AgentState) -> Dict:
    """Generate final response incorporating tool result."""
    tool_result = state.get("tool_result", {})
    tool_name = state.get("selected_tool", "")
    user_input = state.get("user_input", "")
    provider = state.get("provider", "mock")
    model = state.get("model") or None
    system_prompt = state.get("system_prompt", "You are a helpful AI assistant.")

    # Build a prompt that includes the tool result
    if tool_result.get("success", False):
        result_data = tool_result.get("result", {})
        tool_summary = _format_tool_result(tool_name, result_data)
        enhanced_prompt = (
            f"The user asked: {user_input}\n\n"
            f"I used the {tool_name} tool and got this result:\n{tool_summary}\n\n"
            f"Please provide a clear, helpful response that includes this information."
        )
    else:
        enhanced_prompt = (
            f"The user asked: {user_input}\n\n"
            f"I tried to use the {tool_name} tool but it failed: {tool_result.get('error', 'unknown error')}\n\n"
            f"Please acknowledge the error and provide what help you can."
        )

    messages = [LLMMessage(role="user", content=enhanced_prompt)]
    trace = _add_trace(state, "llm_started", f"provider={provider} with_tool_result")

    start = time.perf_counter()
    llm_response = await invoke_with_fallback(
        messages=messages,
        requested_provider=provider,
        model=model,
        system_prompt=system_prompt,
    )
    latency_ms = int((time.perf_counter() - start) * 1000)

    if llm_response.success:
        trace = _add_trace(
            {"trace": trace}, "llm_completed",
            f"provider={llm_response.provider}"
        )
        trace = _add_trace({"trace": trace}, "execution_completed", "status=completed")
        return {
            "response": llm_response.content,
            "actual_provider": llm_response.provider,
            "actual_model": llm_response.model,
            "fallback_used": llm_response.fallback_used,
            "fallback_reason": llm_response.fallback_reason,
            "execution_status": "completed",
            "latency_ms": latency_ms,
            "trace": trace,
        }
    else:
        # If LLM fails but we have tool result, still surface the data
        trace = _add_trace({"trace": trace}, "execution_completed", "status=partial")
        result_data = tool_result.get("result", {})
        fallback_content = f"Tool result: {_format_tool_result(tool_name, result_data)}"
        return {
            "response": fallback_content,
            "actual_provider": "none",
            "actual_model": "none",
            "execution_status": "completed",
            "latency_ms": latency_ms,
            "trace": trace,
        }


def _format_tool_result(tool_name: str, result: Dict) -> str:
    """Format a tool result as a readable string for LLM context."""
    if tool_name == "calculator":
        return f"{result.get('expression', '')} = {result.get('result', '')}"
    elif tool_name == "current_time":
        return (
            f"Current time in {result.get('timezone', 'UTC')}: "
            f"{result.get('time', '')} on {result.get('date', '')} "
            f"({result.get('day_of_week', '')})"
        )
    elif tool_name == "text_stats":
        return (
            f"Characters: {result.get('characters', 0)}, "
            f"Words: {result.get('words', 0)}, "
            f"Sentences: {result.get('sentences', 0)}"
        )
    return str(result)
