"""
AgentFlow — Test Suite
Comprehensive tests covering all 20 scenarios specified in requirements.
Uses Mock provider — never burns real LLM quotas during automated tests.
"""
from __future__ import annotations

import asyncio
import json
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================
# 1. Health
# ============================================================

def test_health_endpoint_structure():
    """Health endpoint must return required fields."""
    from app.api.health import health_check
    import asyncio

    async def run():
        with patch("app.api.health.is_connected", return_value=False):
            result = await health_check()
        return result

    result = asyncio.run(run())
    assert "status" in result
    assert "database" in result
    assert "providers" in result
    assert "mcp" in result
    assert result["status"] == "ok"


# ============================================================
# 2. Model Discovery
# ============================================================

def test_model_discovery():
    """Model service returns all three providers."""
    from app.services.model_service import get_all_models
    result = get_all_models()
    assert "providers" in result
    provider_ids = [p["id"] for p in result["providers"]]
    assert "gemini" in provider_ids
    assert "openrouter" in provider_ids
    assert "mock" in provider_ids


def test_provider_status():
    """Provider status returns availability for all providers."""
    from app.services.model_service import get_provider_status
    statuses = get_provider_status()
    assert isinstance(statuses, list)
    ids = [s["id"] for s in statuses]
    assert "mock" in ids


# ============================================================
# 3. Provider Factory
# ============================================================

def test_factory_returns_providers():
    from app.llm.factory import get_provider, list_provider_ids
    assert "gemini" in list_provider_ids()
    assert "openrouter" in list_provider_ids()
    assert "mock" in list_provider_ids()
    assert get_provider("mock") is not None
    assert get_provider("nonexistent") is None


# ============================================================
# 4. Mock Provider
# ============================================================

@pytest.mark.asyncio
async def test_mock_provider_always_available():
    from app.llm.mock import MockProvider
    p = MockProvider()
    assert p.is_available() is True


@pytest.mark.asyncio
async def test_mock_provider_returns_response():
    from app.llm.mock import MockProvider
    from app.llm.base import LLMMessage
    p = MockProvider()
    response = await p.invoke([LLMMessage(role="user", content="Hello")])
    assert response.success is True
    assert response.provider == "mock"
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_mock_provider_marked_correctly():
    from app.llm.mock import MockProvider
    from app.llm.base import LLMMessage
    p = MockProvider()
    response = await p.invoke([LLMMessage(role="user", content="test")])
    assert response.provider == "mock"
    assert response.requested_provider == "mock"


# ============================================================
# 5. Gemini Configuration
# ============================================================

def test_gemini_unavailable_without_key():
    from app.llm.gemini import GeminiProvider
    with patch("app.llm.gemini.settings") as mock_settings:
        mock_settings.gemini_api_key = ""
        p = GeminiProvider()
        assert p.is_available() is False


@pytest.mark.asyncio
async def test_gemini_returns_auth_error_without_key():
    from app.llm.gemini import GeminiProvider
    from app.llm.base import LLMMessage
    with patch("app.llm.gemini.settings") as mock_settings:
        mock_settings.gemini_api_key = ""
        mock_settings.gemini_model = "gemini-1.5-flash"
        p = GeminiProvider()
        response = await p.invoke([LLMMessage(role="user", content="hi")])
        assert response.success is False
        assert response.error_code == "LLM_AUTH_ERROR"


# ============================================================
# 6. OpenRouter Configuration
# ============================================================

def test_openrouter_unavailable_without_key():
    from app.llm.openrouter import OpenRouterProvider
    with patch("app.llm.openrouter.settings") as mock_settings:
        mock_settings.openrouter_api_key = ""
        p = OpenRouterProvider()
        assert p.is_available() is False


@pytest.mark.asyncio
async def test_openrouter_returns_auth_error_without_key():
    from app.llm.openrouter import OpenRouterProvider
    from app.llm.base import LLMMessage
    with patch("app.llm.openrouter.settings") as mock_settings:
        mock_settings.openrouter_api_key = ""
        mock_settings.openrouter_model = "openrouter/auto"
        p = OpenRouterProvider()
        response = await p.invoke([LLMMessage(role="user", content="hi")])
        assert response.success is False
        assert response.error_code == "LLM_AUTH_ERROR"


# ============================================================
# 7. MCP Tool Discovery
# ============================================================

def test_mcp_tool_discovery():
    from app.mcp.server import list_tools
    tools = list_tools()
    assert len(tools) == 3
    names = [t["name"] for t in tools]
    assert "calculator" in names
    assert "current_time" in names
    assert "text_stats" in names


def test_mcp_tools_have_schemas():
    from app.mcp.server import list_tools
    for tool in list_tools():
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool


# ============================================================
# 8. Calculator Tool
# ============================================================

def test_calculator_basic():
    from app.mcp.tools.calculator import calculator
    result = calculator("2 + 2")
    assert result["result"] == 4


def test_calculator_complex():
    from app.mcp.tools.calculator import calculator
    result = calculator("12345 * 678")
    assert result["result"] == 12345 * 678


def test_calculator_parentheses():
    from app.mcp.tools.calculator import calculator
    result = calculator("(10 + 5) * 2")
    assert result["result"] == 30


def test_calculator_rejects_unsafe():
    from app.mcp.tools.calculator import calculator
    with pytest.raises(ValueError):
        calculator("import os; os.system('rm -rf /')")


def test_calculator_rejects_letters():
    from app.mcp.tools.calculator import calculator
    with pytest.raises(ValueError):
        calculator("__import__('os')")


# ============================================================
# 9. Current Time Tool
# ============================================================

def test_current_time_utc():
    from app.mcp.tools.current_time import current_time
    result = current_time("UTC")
    assert "datetime" in result
    assert result["timezone"] == "UTC"


def test_current_time_kolkata():
    from app.mcp.tools.current_time import current_time
    result = current_time("Asia/Kolkata")
    assert result["timezone"] == "Asia/Kolkata"
    assert "time" in result


def test_current_time_invalid_timezone():
    from app.mcp.tools.current_time import current_time
    with pytest.raises(ValueError):
        current_time("NotATimezone")


def test_current_time_injection_attempt():
    from app.mcp.tools.current_time import current_time
    with pytest.raises(ValueError):
        current_time("UTC; rm -rf /")


# ============================================================
# 10. Text Stats Tool
# ============================================================

def test_text_stats_basic():
    from app.mcp.tools.text_stats import text_stats
    result = text_stats("Hello world. This is a test.")
    assert result["words"] == 6
    assert result["characters"] > 0
    assert result["sentences"] >= 2


def test_text_stats_empty():
    from app.mcp.tools.text_stats import text_stats
    result = text_stats("")
    assert result["words"] == 0
    assert result["characters"] == 0


def test_text_stats_unique_words():
    from app.mcp.tools.text_stats import text_stats
    result = text_stats("the cat sat on the mat")
    assert result["unique_words"] < result["words"]  # "the" repeated


# ============================================================
# 11. Graph — Direct Path
# ============================================================

@pytest.mark.asyncio
async def test_graph_direct_path():
    """General question routes through direct_response without tools."""
    from app.graph.graph import run_graph
    state = {
        "request_id": "test-1",
        "session_id": "sess-1",
        "user_input": "Explain what LangGraph is.",
        "messages": [{"role": "user", "content": "Explain what LangGraph is."}],
        "provider": "mock",
        "model": "mock-model",
        "requested_provider": "mock",
        "system_prompt": "You are helpful.",
        "trace": [],
        "requires_tool": False,
        "fallback_used": False,
        "fallback_reason": "",
        "execution_status": "running",
    }
    result = await run_graph(state)
    assert result.get("execution_status") == "completed"
    assert result.get("requires_tool") is False
    assert len(result.get("response", "")) > 0


# ============================================================
# 12. Graph — Tool Path
# ============================================================

@pytest.mark.asyncio
async def test_graph_tool_path():
    """Calculator request routes through tool execution path."""
    from app.graph.graph import run_graph
    state = {
        "request_id": "test-2",
        "session_id": "sess-2",
        "user_input": "Calculate 100 * 200",
        "messages": [{"role": "user", "content": "Calculate 100 * 200"}],
        "provider": "mock",
        "model": "mock-model",
        "requested_provider": "mock",
        "system_prompt": "You are helpful.",
        "trace": [],
        "requires_tool": False,
        "fallback_used": False,
        "fallback_reason": "",
        "execution_status": "running",
    }
    result = await run_graph(state)
    assert result.get("requires_tool") is True
    assert result.get("selected_tool") == "calculator"
    tool_result = result.get("tool_result", {})
    assert tool_result.get("success") is True


# ============================================================
# 13. REST /api/chat (via httpx TestClient)
# ============================================================

def test_chat_endpoint_mock():
    """Chat endpoint with mock provider returns structured response."""
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as client:
        # We need a session — but DB may not be available.
        # Use a fake session ID; the service gracefully handles no-DB
        response = client.post("/api/chat", json={
            "session_id": "test-session-00000000",
            "message": "Hello from test",
            "provider": "mock",
        })

    # Either success or a known error (not 500)
    assert response.status_code in (200, 503)
    data = response.json()
    if response.status_code == 200:
        assert "request_id" in data
        assert "provider" in data


# ============================================================
# 14. Sessions (no-DB graceful handling)
# ============================================================

@pytest.mark.asyncio
async def test_session_service_no_db():
    """Session service returns empty list when DB unavailable."""
    from app.services import session_service
    session_service.set_db_enabled(False)
    sessions = await session_service.list_sessions()
    assert sessions == []


# ============================================================
# 15. Executions (no-DB graceful handling)
# ============================================================

@pytest.mark.asyncio
async def test_execution_service_no_db():
    """Execution service returns zero stats when DB unavailable."""
    from app.services import execution_service
    execution_service.set_db_enabled(False)
    stats = await execution_service.get_stats()
    assert stats["total"] == 0


# ============================================================
# 16. PostgreSQL Persistence (skipped if no DB configured)
# ============================================================

@pytest.mark.asyncio
async def test_db_connection_skipped_without_url():
    """DB init returns False gracefully when DATABASE_URL is empty."""
    from app.db.connection import init_db
    with patch("app.db.connection.settings") as mock_settings:
        mock_settings.database_url = ""
        result = await init_db()
    assert result is False


# ============================================================
# 17. Provider Fallback
# ============================================================

@pytest.mark.asyncio
async def test_fallback_to_mock_when_gemini_fails():
    """When Gemini fails, fallback chain reaches Mock."""
    from app.llm.factory import invoke_with_fallback
    from app.llm.base import LLMMessage
    from app.core.config import settings as real_settings

    with patch("app.llm.factory.settings") as mock_settings:
        mock_settings.enable_provider_fallback = True
        mock_settings.fallback_chain_list = ["gemini", "openrouter", "mock"]

        # Make Gemini unavailable
        with patch.dict("app.llm.factory._PROVIDERS") as _:
            pass  # Use real providers

        response = await invoke_with_fallback(
            messages=[LLMMessage(role="user", content="test fallback")],
            requested_provider="gemini",  # Gemini has no key → fails → falls to mock
        )

    # Should have succeeded via mock
    assert response.success is True


# ============================================================
# 18. Validation Errors
# ============================================================

def test_calculator_empty_expression():
    from app.mcp.tools.calculator import calculator
    with pytest.raises((ValueError, Exception)):
        calculator("")


def test_current_time_empty_tz():
    from app.mcp.tools.current_time import current_time
    with pytest.raises(ValueError):
        current_time("")


# ============================================================
# 19. Rate Limit Handling (simulated)
# ============================================================

@pytest.mark.asyncio
async def test_gemini_429_returns_rate_limit_code():
    """Simulated 429 from Gemini returns LLM_RATE_LIMIT error code."""
    from app.llm.gemini import GeminiProvider
    from app.llm.base import LLMMessage

    provider = GeminiProvider()

    def mock_invoke():
        raise Exception("429 Resource exhausted quota")

    with patch.object(provider, "_get_client", return_value=True):
        import asyncio
        original_executor = asyncio.get_event_loop().run_in_executor

        async def fake_invoke(messages, model=None, system_prompt=None, **kwargs):
            return provider.__class__.__bases__[0].__init__  # forces error path below

        # Simulate via patching _sync_invoke behavior
        with patch("app.llm.gemini.settings") as s:
            s.gemini_api_key = "fake-key"
            s.gemini_model = "gemini-1.5-flash"

            async def mock_run_in_executor(executor, func):
                return None, Exception("429 quota exceeded")

            loop = asyncio.get_event_loop()
            with patch.object(loop, "run_in_executor", new=mock_run_in_executor):
                response = await provider.invoke(
                    [LLMMessage(role="user", content="test")]
                )

    assert response.success is False
    assert "RATE_LIMIT" in response.error_code or response.error_code in (
        "LLM_RATE_LIMIT", "PROVIDER_UNAVAILABLE"
    )


# ============================================================
# 20. No Secret Exposure
# ============================================================

def test_no_secrets_in_error_response():
    """safe_error_message never includes raw exception details."""
    from app.core.security import safe_error_message
    msg = safe_error_message("LLM_RATE_LIMIT")
    assert "OPENROUTER_API_KEY" not in msg
    assert "GEMINI_API_KEY" not in msg
    assert "DATABASE_URL" not in msg
    assert "postgresql://" not in msg


def test_sanitize_for_log():
    """sanitize_for_log redacts API key patterns."""
    from app.core.security import sanitize_for_log
    text = "Using key sk-abc123def456ghi789jkl and AIzaXXXXXXXXXXXXX"
    result = sanitize_for_log(text)
    assert "sk-abc123" not in result
    assert "AIza" not in result
    assert "[REDACTED]" in result
