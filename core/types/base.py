"""Base Pydantic models for core endpoints and system responses."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class DatabaseStatus(StrEnum):
    """Status enumeration for database connectivity."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UNCONFIGURED = "unconfigured"


class HealthResponse(BaseModel):
    """Schema for GET /health endpoint."""

    status: str = Field(default="healthy", description="Overall system health status")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Current UTC timestamp of response",
    )
    version: str = Field(..., description="Application semantic version")
    environment: str = Field(..., description="Operating environment name")
    database: DatabaseStatus = Field(
        default=DatabaseStatus.UNCONFIGURED,
        description="Database connectivity status",
    )
    details: str | None = Field(
        default=None,
        description="Optional diagnostic context or status note",
    )


class VersionResponse(BaseModel):
    """Schema for GET /version endpoint."""

    name: str = Field(..., description="Application name")
    version: str = Field(..., description="Semantic application version")
    tagline: str = Field(..., description="Project mission or tagline")
    environment: str = Field(..., description="Operating environment")
