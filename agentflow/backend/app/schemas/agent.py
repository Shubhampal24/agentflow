"""Agent Pydantic schemas."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    provider: str = Field("mock")
    model: str = Field("mock-model")
    system_prompt: str = Field("")


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    provider: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    provider: str
    model: str
    system_prompt: str
    created_at: datetime
    updated_at: datetime
