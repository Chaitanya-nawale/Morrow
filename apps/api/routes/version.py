"""Version route providing semantic release and build metadata."""

from fastapi import APIRouter, status

from core.config.settings import get_settings
from core.types.base import VersionResponse

router = APIRouter(tags=["Version"])


@router.get(
    "/version",
    response_model=VersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Application version metadata",
    description="Returns current project version, name, and environment context.",
)
async def get_version() -> VersionResponse:
    """Retrieve semantic version and identity information for Morrow."""
    settings = get_settings()
    return VersionResponse(
        name=settings.app_name,
        version=settings.app_version,
        tagline=settings.app_tagline,
        environment=settings.app_env,
    )
