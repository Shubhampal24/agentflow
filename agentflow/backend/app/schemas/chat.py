"""Chat Pydantic schemas."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=4000)
    provider: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None


class ToolUsed(BaseModel):
    name: str
    status: str
    duration_ms: int
    result: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    success: bool = True
    request_id: str
    session_id: str
    response: str
    provider: str
    model: str
    requested_provider: str
    fallback_used: bool = False
    fallback_reason: str = ""
    tools_used: List[ToolUsed] = []
    execution_id: str
    latency_ms: int
    status: str
    trace: List[Dict[str, Any]] = []
