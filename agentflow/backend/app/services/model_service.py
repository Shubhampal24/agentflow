"""
AgentFlow — Model Discovery Service
Returns available models per provider.
Handles individual provider failures gracefully.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.llm.factory import get_all_providers

logger = logging.getLogger(__name__)


def get_all_models() -> Dict[str, Any]:
    """Return models for all providers. Never fails due to one provider being down."""
    providers = []
    for provider_id, provider in get_all_providers().items():
        try:
            models = provider.list_models()
            providers.append({
                "id": provider_id,
                "available": provider.is_available(),
                "models": models,
            })
        except Exception as exc:
            logger.warning(f"Model discovery failed for {provider_id}: {exc}")
            providers.append({
                "id": provider_id,
                "available": False,
                "models": [],
                "error": "Model discovery failed.",
            })
    return {"providers": providers}


def get_provider_status() -> List[Dict[str, Any]]:
    """Return availability status of each provider."""
    result = []
    for provider_id, provider in get_all_providers().items():
        result.append({
            "id": provider_id,
            "available": provider.is_available(),
        })
    return result
