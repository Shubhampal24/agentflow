"""
AgentFlow — MCP Client
Abstraction layer between LangGraph and the MCP server.
Demonstrates the clear execution path:

LangGraph → MCP Client → MCP Server → Tool → Tool Result → LangGraph
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from app.mcp import server as mcp_server

logger = logging.getLogger(__name__)


class MCPToolResult:
    """Result returned from an MCP tool call."""

    def __init__(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error: str = "",
        duration_ms: int = 0,
    ):
        self.tool_name = tool_name
        self.arguments = arguments
        self.result = result or {}
        self.success = success
        self.error = error
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "result": self.result,
            "success": self.success,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


class MCPClient:
    """
    MCP Client that routes tool calls through the MCP server.
    This is the integration boundary — LangGraph never calls tool functions directly.
    """

    def list_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools from the MCP server."""
        return mcp_server.list_tools()

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """
        Call a tool via the MCP server and return a structured result.

        Path: LangGraph → MCPClient.call_tool → mcp_server.execute_tool → Tool Handler → Result
        """
        start = time.perf_counter()
        logger.info(f"MCP client calling tool: {tool_name}")

        try:
            result = mcp_server.execute_tool(tool_name, arguments)
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.info(f"MCP client tool {tool_name} completed in {duration_ms}ms")
            return MCPToolResult(
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                success=True,
                duration_ms=duration_ms,
            )
        except ValueError as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.error(f"MCP client tool {tool_name} failed: {exc}")
            return MCPToolResult(
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                error=str(exc),
                duration_ms=duration_ms,
            )
        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.error(f"MCP client unexpected error for tool {tool_name}: {exc}")
            return MCPToolResult(
                tool_name=tool_name,
                arguments=arguments,
                success=False,
                error=f"Internal tool error: {type(exc).__name__}",
                duration_ms=duration_ms,
            )


# Singleton client instance
mcp_client = MCPClient()
