"""Session Pydantic schemas."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SessionCreate(BaseModel):
    agent_id: Optional[str] = None
    title: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    agent_id: Optional[str]
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
