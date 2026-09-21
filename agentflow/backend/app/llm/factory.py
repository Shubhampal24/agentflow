"""
AgentFlow — LLM Provider Factory
Creates and manages provider instances.
Implements configurable fallback chain.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

from app.core.config import settings
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.llm.gemini import GeminiProvider
from app.llm.mock import MockProvider
from app.llm.openrouter import OpenRouterProvider

logger = logging.getLogger(__name__)

_PROVIDERS: Dict[str, BaseLLMProvider] = {
    "gemini": GeminiProvider(),
    "openrouter": OpenRouterProvider(),
    "mock": MockProvider(),
}


def get_provider(provider_id: str) -> Optional[BaseLLMProvider]:
    return _PROVIDERS.get(provider_id)


def list_provider_ids() -> List[str]:
    return list(_PROVIDERS.keys())


def get_all_providers() -> Dict[str, BaseLLMProvider]:
    return _PROVIDERS


async def invoke_with_fallback(
    messages: List[LLMMessage],
    requested_provider: str,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    **kwargs,
) -> LLMResponse:
    """
    Attempt to invoke the requested provider.
    If it fails and fallback is enabled, try the fallback chain.
    Never silently claim the primary provider succeeded if fallback occurred.
    """
    primary = get_provider(requested_provider)
    if primary is None:
        logger.warning(f"Unknown provider requested: {requested_provider}. Falling back.")
        primary_id = settings.fallback_provider
        primary = get_provider(primary_id) or _PROVIDERS["mock"]
    else:
        primary_id = requested_provider

    # Try primary
    if primary.is_available():
        response = await primary.invoke(
            messages=messages,
            model=model,
            system_prompt=system_prompt,
            **kwargs,
        )
        response.requested_provider = requested_provider
        if response.success:
            return response
        # Primary failed — log and try fallback
        primary_error = response.error_code
        logger.warning(
            f"Provider {primary_id} failed with {primary_error}. Fallback enabled={settings.enable_provider_fallback}"
        )
    else:
        primary_error = "PROVIDER_UNAVAILABLE"
        logger.warning(f"Provider {primary_id} not available (no credentials).")
        response = LLMResponse(
            content="",
            provider=primary_id,
            model=model or "",
            success=False,
            error_code=primary_error,
            error_message=f"{primary_id} is not configured.",
            requested_provider=requested_provider,
        )

    if not settings.enable_provider_fallback:
        return response

    # Walk fallback chain
    for fallback_id in settings.fallback_chain_list:
        if fallback_id == primary_id:
            continue
        fallback = get_provider(fallback_id)
        if fallback is None or not fallback.is_available():
            continue
        logger.info(f"Attempting fallback to: {fallback_id}")
        fb_response = await fallback.invoke(
            messages=messages,
            model=None,  # Use fallback provider's default model
            system_prompt=system_prompt,
            **kwargs,
        )
        if fb_response.success:
            fb_response.requested_provider = requested_provider
            fb_response.fallback_used = True
            fb_response.fallback_reason = f"{primary_id} failed: {primary_error}"
            logger.info(f"Fallback to {fallback_id} succeeded.")
            return fb_response

    # All failed — return last error
    logger.error("All providers in fallback chain failed.")
    return response
