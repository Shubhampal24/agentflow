"""MCP tools discovery endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from app.mcp.server import list_tools

router = APIRouter(prefix="/api")


@router.get("/tools")
async def get_tools():
    """Return all available MCP tools dynamically from server registry."""
    return {"tools": list_tools()}
