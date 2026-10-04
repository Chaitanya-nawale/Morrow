"""API routes package."""

from apps.api.routes.health import router as health_router
from apps.api.routes.version import router as version_router

__all__ = ["health_router", "version_router"]
