"""
AgentFlow — MCP Server
Registry of available tools. Provides tool discovery and execution.
Acts as the local MCP server that the MCP client calls through.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.mcp.tools.calculator import calculator, TOOL_DEFINITION as CALC_DEF
from app.mcp.tools.current_time import current_time, TOOL_DEFINITION as TIME_DEF
from app.mcp.tools.text_stats import text_stats, TOOL_DEFINITION as STATS_DEF

logger = logging.getLogger(__name__)

# ── Tool Registry ─────────────────────────────────────────────────────────────

_TOOL_REGISTRY: Dict[str, Dict] = {
    "calculator": {
        "definition": CALC_DEF,
        "handler": calculator,
        "input_key": "expression",
    },
    "current_time": {
        "definition": TIME_DEF,
        "handler": current_time,
        "input_key": "timezone",
    },
    "text_stats": {
        "definition": STATS_DEF,
        "handler": text_stats,
        "input_key": "text",
    },
}


def list_tools() -> List[Dict[str, Any]]:
    """Return a list of all available MCP tool definitions."""
    return [entry["definition"] for entry in _TOOL_REGISTRY.values()]


def get_tool_definition(tool_name: str) -> Optional[Dict[str, Any]]:
    """Get the definition for a specific tool."""
    entry = _TOOL_REGISTRY.get(tool_name)
    return entry["definition"] if entry else None


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool by name with the given arguments.
    Raises ValueError for unknown tools or invalid arguments.
    """
    entry = _TOOL_REGISTRY.get(tool_name)
    if entry is None:
        raise ValueError(f"Unknown tool: {tool_name!r}")

    handler = entry["handler"]
    logger.info(f"MCP server executing tool: {tool_name}", extra={"arguments": str(arguments)[:100]})

    try:
        result = handler(**arguments)
        logger.info(f"MCP tool {tool_name} completed successfully.")
        return result
    except Exception as exc:
        logger.error(f"MCP tool {tool_name} failed: {exc}")
        raise
