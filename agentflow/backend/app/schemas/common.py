"""Common Pydantic schemas."""
from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    request_id: Optional[str] = None


class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "OK"
