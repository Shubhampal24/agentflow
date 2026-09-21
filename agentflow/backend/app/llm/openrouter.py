"""
AgentFlow — OpenRouter LLM Provider
Uses OpenAI-compatible API. Supports dynamic model discovery.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterProvider(BaseLLMProvider):
    provider_id = "openrouter"

    def is_available(self) -> bool:
        return bool(settings.openrouter_api_key)

    def list_models(self) -> List[Dict[str, Any]]:
        # Static fallback list — dynamic discovery attempted in model_service
        return [
            {
                "id": "openrouter/auto",
                "name": "Auto (Best Free Available)",
                "provider": "openrouter",
                "free": True,
                "available": self.is_available(),
                "capabilities": ["text"],
            },
            {
                "id": "mistralai/mistral-7b-instruct:free",
                "name": "Mistral 7B Instruct (Free)",
                "provider": "openrouter",
                "free": True,
                "available": self.is_available(),
                "capabilities": ["text"],
            },
            {
                "id": "meta-llama/llama-3.1-8b-instruct:free",
                "name": "Llama 3.1 8B Instruct (Free)",
                "provider": "openrouter",
                "free": True,
                "available": self.is_available(),
                "capabilities": ["text"],
            },
        ]

    async def invoke(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        import asyncio

        if not settings.openrouter_api_key:
            return LLMResponse(
                content="",
                provider="openrouter",
                model=model or settings.openrouter_model,
                success=False,
                error_code="LLM_AUTH_ERROR",
                error_message="OpenRouter API key not configured.",
                requested_provider="openrouter",
            )

        model_id = model or settings.openrouter_model

        def _sync_invoke():
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=settings.openrouter_api_key,
                    base_url=OPENROUTER_BASE_URL,
                )

                # Build messages
                or_messages = []
                if system_prompt:
                    or_messages.append({"role": "system", "content": system_prompt})
                for msg in messages:
                    or_messages.append({"role": msg.role, "content": msg.content})

                response = client.chat.completions.create(
                    model=model_id,
                    messages=or_messages,
                    max_tokens=1024,
                )
                content = response.choices[0].message.content or ""
                usage = {}
                if response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                return content, usage, None
            except Exception as exc:
                return None, {}, exc

        loop = asyncio.get_event_loop()
        text, usage, error = await loop.run_in_executor(None, _sync_invoke)

        if error is not None:
            err_str = str(error)
            if "429" in err_str or "rate" in err_str.lower():
                code = "LLM_RATE_LIMIT"
            elif "401" in err_str or "auth" in err_str.lower():
                code = "LLM_AUTH_ERROR"
            else:
                code = "PROVIDER_UNAVAILABLE"
            logger.error(f"OpenRouter invoke error: {error}")
            return LLMResponse(
                content="",
                provider="openrouter",
                model=model_id,
                success=False,
                error_code=code,
                error_message=err_str[:200],
                requested_provider="openrouter",
            )

        return LLMResponse(
            content=text or "",
            provider="openrouter",
            model=model_id,
            usage=usage,
            requested_provider="openrouter",
            success=True,
        )
