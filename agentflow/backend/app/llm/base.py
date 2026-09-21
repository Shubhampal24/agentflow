"""
AgentFlow — LLM Provider Base Interface
All providers implement this abstract class.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LLMMessage:
    """Normalized message for LLM invocation."""
    role: str  # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    """Normalized response from any LLM provider."""
    content: str
    provider: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Fallback tracking
    requested_provider: str = ""
    fallback_used: bool = False
    fallback_reason: str = ""

    # Error tracking
    success: bool = True
    error_code: str = ""
    error_message: str = ""


class BaseLLMProvider(ABC):
    """Abstract base for all LLM providers."""

    provider_id: str = ""

    @abstractmethod
    async def invoke(
        self,
        messages: List[LLMMessage],
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> LLMResponse:
        """Send messages and return a normalized LLMResponse."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this provider has credentials configured."""

    @abstractmethod
    def list_models(self) -> List[Dict[str, Any]]:
        """Return a list of available model descriptors."""
