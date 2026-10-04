"""Application settings management using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Morrow configuration settings loaded from environment or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="Morrow", description="Application name")
    app_env: Literal["development", "testing", "production"] = Field(
        default="development", description="Current operating environment"
    )
    app_version: str = Field(default="0.1.0", description="Semantic application version")
    app_tagline: str = Field(
        default="Evidence-Driven Long-Horizon Agentic Memory",
        description="Morrow project tagline",
    )
    debug: bool = Field(default=False, description="Debug mode toggle")

    # API Server
    api_host: str = Field(default="0.0.0.0", description="Host address to bind API")
    api_port: int = Field(default=8000, description="Port number to bind API")

    # Database (PostgreSQL / Neon with pgvector)
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/morrow",
        description="Async SQLAlchemy database connection string",
    )

    # Logging
    log_level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR")
    log_format: Literal["console", "json"] = Field(
        default="console", description="Log format: console or json"
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings."""
    return Settings()
