"""Execution Pydantic schemas."""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ExecutionResponse(BaseModel):
    id: str
    session_id: str
    request: Optional[str]
    response: Optional[str]
    provider: Optional[str]
    model: Optional[str]
    requested_provider: Optional[str]
    fallback_used: bool = False
    fallback_reason: Optional[str]
    status: str
    latency_ms: Optional[int]
    error_code: Optional[str]
    trace: Optional[List[Dict[str, Any]]]
    created_at: datetime
