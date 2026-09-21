"""Agents CRUD endpoints."""
from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, HTTPException

from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from app.services import agent_service

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


@router.post("/agents", response_model=AgentResponse)
async def create_agent(body: AgentCreate):
    try:
        agent = await agent_service.create_agent(
            name=body.name,
            description=body.description,
            provider=body.provider,
            model=body.model,
            system_prompt=body.system_prompt,
        )
        return agent
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"code": "DATABASE_ERROR", "message": str(exc)})
    except Exception as exc:
        logger.exception(f"Create agent error: {exc}")
        raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": "Failed to create agent."})


@router.get("/agents")
async def list_agents():
    agents = await agent_service.list_agents()
    return {"agents": agents}


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    agent = await agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail={"code": "AGENT_NOT_FOUND", "message": "Agent not found."})
    return agent


@router.patch("/agents/{agent_id}")
async def update_agent(agent_id: str, body: AgentUpdate):
    try:
        updated = await agent_service.update_agent(agent_id, **body.model_dump(exclude_none=True))
        if not updated:
            raise HTTPException(status_code=404, detail={"code": "AGENT_NOT_FOUND", "message": "Agent not found."})
        return updated
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail={"code": "DATABASE_ERROR", "message": str(exc)})
