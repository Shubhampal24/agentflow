"""
AgentFlow — LangGraph StateGraph Builder
Assembles the complete agent graph.

Graph structure:
START → analyze_request → [route] → direct_response → END
                                  → select_tool → execute_mcp_tool → final_response → END
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from langgraph.graph import StateGraph, END, START

from app.graph.nodes import (
    analyze_request,
    select_tool,
    execute_mcp_tool,
    direct_response,
    final_response,
)
from app.graph.routing import route_after_analysis
from app.graph.state import AgentState

logger = logging.getLogger(__name__)


def build_graph() -> StateGraph:
    """Construct and compile the AgentFlow StateGraph."""
    graph = StateGraph(AgentState)

    # ── Nodes ─────────────────────────────────────────────────
    graph.add_node("analyze_request", analyze_request)
    graph.add_node("select_tool", select_tool)
    graph.add_node("execute_mcp_tool", execute_mcp_tool)
    graph.add_node("direct_response", direct_response)
    graph.add_node("final_response", final_response)

    # ── Edges ─────────────────────────────────────────────────
    graph.add_edge(START, "analyze_request")

    graph.add_conditional_edges(
        "analyze_request",
        route_after_analysis,
        {
            "direct_response": "direct_response",
            "tool_required": "select_tool",
        },
    )

    graph.add_edge("select_tool", "execute_mcp_tool")
    graph.add_edge("execute_mcp_tool", "final_response")
    graph.add_edge("direct_response", END)
    graph.add_edge("final_response", END)

    return graph.compile()


# ── Singleton compiled graph ──────────────────────────────────────────────────
_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
        logger.info("LangGraph StateGraph compiled successfully.")
    return _compiled_graph


async def run_graph(initial_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the compiled graph with an initial state.
    Returns the final state dict.
    """
    graph = get_graph()
    try:
        final_state = await graph.ainvoke(initial_state)
        return dict(final_state)
    except Exception as exc:
        logger.exception(f"Graph execution failed: {exc}")
        raise
