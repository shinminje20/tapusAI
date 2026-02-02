"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars like telegram settings
    )

    # Application
    app_name: str = "TapusAI Waitlist API"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./tapusai.db"

    # Waitlist defaults
    default_avg_turn_time_minutes: int = 15


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
