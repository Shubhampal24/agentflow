"""Executions read endpoints."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.services import execution_service

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


@router.get("/executions")
async def list_executions():
    executions = await execution_service.list_executions()
    stats = await execution_service.get_stats()
    return {"executions": executions, "stats": stats}


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    execution = await execution_service.get_execution(execution_id)
    if not execution:
        raise HTTPException(
            status_code=404,
            detail={"code": "EXECUTION_NOT_FOUND", "message": "Execution not found."},
        )
    return execution
