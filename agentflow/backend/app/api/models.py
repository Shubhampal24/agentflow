"""Models and providers discovery endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from app.services.model_service import get_all_models, get_provider_status

router = APIRouter(prefix="/api")


@router.get("/models")
async def list_models():
    """Return all available models per provider. Never fails due to one provider being down."""
    return get_all_models()


@router.get("/providers")
async def list_providers():
    """Return provider availability status."""
    return {"providers": get_provider_status()}
