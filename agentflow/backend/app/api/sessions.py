"""Sessions CRUD endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.session import SessionCreate, SessionResponse
from app.services import session_service, execution_service

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


@router.post("/sessions")
async def create_session(body: SessionCreate):
    try:
        session = await session_service.create_session(
            agent_id=body.agent_id,
            title=body.title,
        )
        return session
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"code": "DATABASE_ERROR", "message": str(exc)})
    except Exception as exc:
        logger.exception(f"Create session error: {exc}")
        raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": "Failed to create session."})


@router.get("/sessions")
async def list_sessions():
    sessions = await session_service.list_sessions()
    return {"sessions": sessions}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail={"code": "SESSION_NOT_FOUND", "message": "Session not found."})
    return session


@router.get("/sessions/{session_id}/executions")
async def get_session_executions(session_id: str):
    executions = await execution_service.list_session_executions(session_id)
    return {"executions": executions}
