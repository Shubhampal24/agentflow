"""
AgentFlow — Gemini LLM Provider
Uses google-generativeai SDK. Returns structured errors on failure.
Never silently swallows provider errors.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    provider_id = "gemini"

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not settings.gemini_api_key:
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            self._client = genai
            return self._client
        except Exception as exc:
            logger.error(f"Gemini client init failed: {exc}")
            return None

    def is_available(self) -> bool:
        return bool(settings.gemini_api_key)

    def list_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "gemini-1.5-flash",
                "name": "Gemini 1.5 Flash",
                "provider": "gemini",
                "free": True,
                "available": self.is_available(),
                "capabilities": ["text"],
            },
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "provider": "gemini",
                "free": False,
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

        client = self._get_client()
        if client is None:
            return LLMResponse(
                content="",
                provider="gemini",
                model=model or settings.gemini_model,
                success=False,
                error_code="LLM_AUTH_ERROR",
                error_message="Gemini API key not configured.",
                requested_provider="gemini",
            )

        model_id = model or settings.gemini_model

        def _sync_invoke():
            try:
                import google.generativeai as genai

                # Build system instruction
                sys_instr = system_prompt or "You are a helpful AI assistant."

                gemini_model = genai.GenerativeModel(
                    model_name=model_id,
                    system_instruction=sys_instr,
                )

                # Convert messages to Gemini format
                history = []
                last_user_msg = ""
                for msg in messages:
                    if msg.role == "user":
                        last_user_msg = msg.content
                    elif msg.role == "assistant":
                        history.append({"role": "model", "parts": [msg.content]})

                if not last_user_msg:
                    last_user_msg = messages[-1].content if messages else ""

                response = gemini_model.generate_content(last_user_msg)
                return response.text, None
            except Exception as exc:
                return None, exc

        loop = asyncio.get_event_loop()
        text, error = await loop.run_in_executor(None, _sync_invoke)

        if error is not None:
            err_str = str(error)
            code = "LLM_RATE_LIMIT" if "429" in err_str or "quota" in err_str.lower() else "PROVIDER_UNAVAILABLE"
            logger.error(f"Gemini invoke error: {error}")
            return LLMResponse(
                content="",
                provider="gemini",
                model=model_id,
                success=False,
                error_code=code,
                error_message=err_str[:200],
                requested_provider="gemini",
            )

        return LLMResponse(
            content=text or "",
            provider="gemini",
            model=model_id,
            usage={},
            requested_provider="gemini",
            success=True,
        )
