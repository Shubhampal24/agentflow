"""
AgentFlow — Application Configuration
Uses pydantic-settings to load from environment variables / .env file.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ─────────────────────────────────────────────────
    app_name: str = "AgentFlow"
    app_env: str = "development"
    app_version: str = "1.0.0"

    # ── Server ───────────────────────────────────────────────
    host: str = "127.0.0.1"
    port: int = 8000

    # ── Database ─────────────────────────────────────────────
    database_url: str = ""

    # ── CORS ─────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    # ── Gemini ───────────────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # ── OpenRouter ───────────────────────────────────────────
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/auto"

    # ── Provider defaults ────────────────────────────────────
    default_provider: str = "mock"
    default_model: str = "mock-model"
    enable_provider_fallback: bool = True
    fallback_provider: str = "mock"
    fallback_chain: str = "gemini,openrouter,mock"

    @property
    def fallback_chain_list(self) -> List[str]:
        return [p.strip() for p in self.fallback_chain.split(",") if p.strip()]

    # ── MCP ──────────────────────────────────────────────────
    mcp_enabled: bool = True

    # ── Limits ───────────────────────────────────────────────
    max_message_length: int = 4000

    # ── Derived helpers ──────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def has_openrouter(self) -> bool:
        return bool(self.openrouter_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
