"""Application configuration using pydantic-settings.

REQ-SEC-004: Configuration for authentication and RBAC.
REQ-NOTIF-001: SMS adapter configuration for notifications.
NFR-SEC-012: Session security settings (token expiry).
NFR-SEC-022: Secrets managed via environment variables.
"""

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

    # JWT Authentication (REQ-SEC-004, NFR-SEC-012)
    # NFR-SEC-022: Secrets from environment variables
    jwt_secret_key: str = ""  # Empty string means generate random (dev only)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15  # NFR-SEC-012: Tokens must expire
    refresh_token_expire_days: int = 7  # NFR-SEC-012: Refresh mechanism

    # SMS Configuration (REQ-NOTIF-001)
    # SMS_ADAPTER: "mock" for testing, "twilio" for production
    sms_adapter: str = "mock"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    restaurant_name: str = "the restaurant"

    # Reminder Configuration (REQ-NOTIF-002)
    # AC-NOTIF-003: Automated reminder/status updates
    reminder_minutes_before: int = 10  # Send reminder X minutes before estimated seating
    reminder_check_interval_seconds: int = 60  # Check for due reminders every X seconds


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
