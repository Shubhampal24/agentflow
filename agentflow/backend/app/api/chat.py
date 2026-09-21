"""
AgentFlow — Chat endpoint
POST /api/chat — main agent interaction endpoint.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.core.security import safe_error_message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent_runner import run_chat

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


@router.post("/chat")
async def chat(body: ChatRequest):
    """
    Run the LangGraph agent for a user message.
    Returns full response with provider metadata, tool usage, and trace.
    """
    # Input validation
    if len(body.message) > settings.max_message_length:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "VALIDATION_ERROR",
                "message": f"Message too long. Max {settings.max_message_length} characters.",
            },
        )

    try:
        result = await run_chat(
            session_id=body.session_id,
            message=body.message,
            provider=body.provider,
            model=body.model,
            system_prompt=body.system_prompt,
        )
    except Exception as exc:
        logger.exception(f"Chat endpoint error: {exc}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": safe_error_message("INTERNAL_ERROR"),
            },
        )

    if not result.get("success", True) and result.get("error_code"):
        code = result.get("error_code", "INTERNAL_ERROR")
        # Return structured error but still 200 for client-side handling
        return {
            "success": False,
            "request_id": result.get("request_id", ""),
            "session_id": body.session_id,
            "execution_id": result.get("execution_id", ""),
            "latency_ms": result.get("latency_ms", 0),
            "status": "failed",
            "error": {
                "code": code,
                "message": safe_error_message(code),
            },
        }

    return result
