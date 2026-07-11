import os
import secrets
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env values override any environment-level overrides (such as preset placeholders in the host shell)
# Skip during testing to allow test configuration to apply.
if os.environ.get("APP_ENV") != "test":
    load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=True)

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_name: str = "AgentFlow AI"

    # Database
    database_url: str = Field(alias="DATABASE_URL")
    sync_database_url: str | None = Field(default=None, alias="SYNC_DATABASE_URL")

    # Vector DB
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(default=None, alias="QDRANT_API_KEY")

    # JWT
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_previous_secret: str | None = Field(default=None, alias="JWT_PREVIOUS_SECRET")
    jwt_kid_current: str = Field(default="v2", alias="JWT_KID_CURRENT")
    jwt_kid_previous: str = Field(default="v1", alias="JWT_KID_PREVIOUS")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=1440, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=30, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # AI
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL"
    )
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    ai_model: str = Field(default="deepseek/deepseek-v4-flash:free", alias="AI_MODEL")
    ai_fallback_model: str = Field(default="deepseek/deepseek-v4-flash:free", alias="AI_FALLBACK_MODEL")

    # Email
    smtp_host: str = Field(default="localhost", alias="SMTP_HOST")
    smtp_port: int = Field(default=1025, alias="SMTP_PORT")
    smtp_user: str | None = Field(default=None, alias="SMTP_USER")
    smtp_password: str | None = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str = Field(default="noreply@agentflow.local", alias="SMTP_FROM")
    sendgrid_api_key: str | None = Field(default=None, alias="SENDGRID_API_KEY")
    email_provider: str = Field(default="smtp", alias="EMAIL_PROVIDER")

    # Frontend & CORS
    frontend_url: str = Field(default="http://localhost:3000", alias="FRONTEND_URL")
    allowed_origins: str = Field(default="http://localhost:3000", alias="ALLOWED_ORIGINS")
    allowed_hosts: str = Field(default="localhost,127.0.0.1", alias="ALLOWED_HOSTS")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Rate limiting
    ai_rate_limit_per_minute: int = Field(default=100, alias="AI_RATE_LIMIT_PER_MINUTE")
    api_rate_limit_per_minute: int = Field(default=1000, alias="API_RATE_LIMIT_PER_MINUTE")
    auth_rate_limit_per_minute: int = Field(default=30, alias="AUTH_RATE_LIMIT_PER_MINUTE")

    # Widget
    widget_ws_url: str = Field(default="ws://localhost:8000", alias="WIDGET_WS_URL")
    widget_api_key: str = Field(default="", alias="WIDGET_API_KEY")
    public_api_key: str = Field(default="", alias="PUBLIC_API_KEY")

    # Cloud storage
    s3_bucket: str | None = Field(default=None, alias="S3_BUCKET")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")
    s3_access_key: str | None = Field(default=None, alias="S3_ACCESS_KEY")
    s3_secret_key: str | None = Field(default=None, alias="S3_SECRET_KEY")
    s3_endpoint: str | None = Field(default=None, alias="S3_ENDPOINT")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # OpenTelemetry
    otel_enabled: bool = Field(default=False, alias="OTEL_ENABLED")
    otel_exporter_otlp_endpoint: str | None = Field(default=None, alias="OTEL_EXPORTER_OTLP_ENDPOINT")

    # Stripe
    stripe_api_key: str | None = Field(default=None, alias="STRIPE_API_KEY")
    stripe_webhook_secret: str | None = Field(default=None, alias="STRIPE_WEBHOOK_SECRET")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32 and v != "replace-with-very-long-random-secret-min-32-char":
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return v

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
