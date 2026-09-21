"""
AgentFlow — Security Utilities
Request ID generation, input sanitization, safe error responses.
"""
from __future__ import annotations

import re
import uuid


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def generate_id() -> str:
    """Generate a UUID string (for sessions, executions, etc.)."""
    return str(uuid.uuid4())


def sanitize_for_log(text: str, max_length: int = 200) -> str:
    """Truncate and redact text for safe logging."""
    if not text:
        return ""
    text = text[:max_length]
    # Redact anything that looks like an API key / token
    text = re.sub(r"(sk-|AIza)[A-Za-z0-9_\-]{10,}", "[REDACTED]", text)
    return text


SAFE_ERROR_MESSAGES = {
    "VALIDATION_ERROR": "The request could not be validated.",
    "PROVIDER_UNAVAILABLE": "The selected provider is temporarily unavailable.",
    "LLM_RATE_LIMIT": "The selected model is temporarily rate limited. Please try again shortly.",
    "LLM_AUTH_ERROR": "Provider authentication failed. Please check your API key configuration.",
    "MODEL_NOT_FOUND": "The requested model could not be found.",
    "MCP_TOOL_ERROR": "The requested tool could not be executed.",
    "DATABASE_ERROR": "A database error occurred.",
    "AGENT_ERROR": "The agent encountered an error processing your request.",
    "INTERNAL_ERROR": "An internal error occurred.",
}


def safe_error_message(code: str) -> str:
    return SAFE_ERROR_MESSAGES.get(code, SAFE_ERROR_MESSAGES["INTERNAL_ERROR"])
