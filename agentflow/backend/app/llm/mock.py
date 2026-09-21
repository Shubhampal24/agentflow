"""
AgentFlow — Mock LLM Provider
Always available. Never requires credentials.
Clearly marked as mock in all responses.
"""
from __future__ import annotations

import asyncio
import re
from typing import Any, Dict, List, Optional

from app.llm.base import BaseLLMProvider, LLMMessage, LLMResponse


_TOOL_PATTERNS = [
    (r"\bcalculat", "calculator"),
    (r"\b\d+\s*[\+\-\*\/\%\^]\s*\d+", "calculator"),
    (r"\btime\b|\bclock\b|\btimezone\b", "current_time"),
    (r"\bword[s]?\b.*count|\bcount.*word|\btext.?stat|\bsentence", "text_stats"),
]

_RESPONSES = {
    "calculator": "I can calculate that for you using the calculator tool.",
    "current_time": "Let me check the current time for you.",
    "text_stats": "I'll analyze that text for you.",
    "general": (
        "This is a mock response from AgentFlow. "
        "I am the Mock provider and I'm confirming that the LangGraph agent pipeline, "
        "REST API, and persistence layer are all working correctly. "
        "Configure a real provider (Gemini or OpenRouter) to get actual AI responses."
    ),
}


class MockProvider(BaseLLMProvider):
    provider_id = "mock"

    def is_available(self) -> bool:
        return True

    def list_models(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "mock-model",
                "name": "Mock Model",
                "provider": "mock",
                "free": True,
                "available": True,
                "capabilities": ["text"],
            }
        ]

    async def invoke(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        await asyncio.sleep(0.05)  # Tiny delay to simulate latency

        # Determine intent from last user message
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        intent = self._classify(last_user)
        content = _RESPONSES.get(intent, _RESPONSES["general"])

        return LLMResponse(
            content=content,
            provider="mock",
            model=model or "mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            metadata={"intent": intent},
            requested_provider="mock",
            success=True,
        )

    def _classify(self, text: str) -> str:
        lower = text.lower()
        for pattern, tool in _TOOL_PATTERNS:
            if re.search(pattern, lower):
                return tool
        return "general"
