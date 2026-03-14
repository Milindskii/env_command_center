"""
core/config.py
──────────────
Application-wide settings loaded from environment variables via pydantic-settings.

All secrets and deployment-specific values live in the `.env` file and are
validated at startup so that misconfiguration fails fast.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Immutable, validated application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ────────────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:milind7841@localhost:5432/env_command_center"
    )

    # ── External APIs ───────────────────────────────────────────────────
    AQI_API_KEY: str = "e5f80640f2cc88a05191fc2dfbcd2dd3667c6faf"

    # ── Monitoring targets ──────────────────────────────────────────────
    MONITOR_CITIES: str = "delhi,mumbai,bangalore,chennai,kolkata"

    @property
    def city_list(self) -> list[str]:
        """Return monitored cities as a clean list."""
        return [c.strip() for c in self.MONITOR_CITIES.split(",") if c.strip()]


# Singleton — import this everywhere instead of re-instantiating.
settings = Settings()