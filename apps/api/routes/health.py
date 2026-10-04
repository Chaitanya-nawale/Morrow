"""Health check route for system diagnostics and monitoring."""

from datetime import UTC, datetime

from fastapi import APIRouter, status

from core.config.settings import get_settings
from core.types.base import DatabaseStatus, HealthResponse
from db.session import check_db_connection

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System health status",
    description="Returns current operational status, environment info, and database connectivity.",
)
async def get_health() -> HealthResponse:
    """Retrieve overall application and component health status."""
    settings = get_settings()
    db_status = await check_db_connection()

    overall_status = "healthy"
    details = None
    if db_status == DatabaseStatus.DISCONNECTED:
        details = "Database connection is unavailable."

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(UTC),
        version=settings.app_version,
        environment=settings.app_env,
        database=db_status,
        details=details,
    )
