"""
AgentFlow — LangGraph Routing
Conditional edge functions that determine the graph path.
"""
from __future__ import annotations

from app.graph.state import AgentState


def route_after_analysis(state: AgentState) -> str:
    """
    After analyze_request node, decide whether to:
    - call a tool (tool_required)
    - respond directly (direct_response)
    """
    if state.get("requires_tool", False):
        return "tool_required"
    return "direct_response"
