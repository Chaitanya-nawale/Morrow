"""FastAPI application initialization and lifespan management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routes.health import router as health_router
from apps.api.routes.version import router as version_router
from core.config.settings import get_settings
from core.logging.logger import get_logger, setup_logging
from db.session import close_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager handling startup and graceful shutdown."""
    settings = get_settings()
    setup_logging(level=settings.log_level, log_format=settings.log_format)
    logger.info(
        "Starting %s v%s in %s mode", settings.app_name, settings.app_version, settings.app_env
    )

    try:
        yield
    finally:
        logger.info("Shutting down %s...", settings.app_name)
        await close_db()
        logger.info("Database connections closed successfully.")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Evidence-Driven Long-Horizon Agentic Memory System",
        docs_url="/docs" if settings.debug or settings.app_env != "production" else None,
        redoc_url="/redoc" if settings.debug or settings.app_env != "production" else None,
        lifespan=lifespan,
    )

    # Cross-Origin Resource Sharing (CORS) configuration
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"]
        if settings.debug
        else ["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routes at root level for /health and /version
    application.include_router(health_router)
    application.include_router(version_router)

    # Also mount under /api/v1 prefix for consistency with future API extensions
    application.include_router(health_router, prefix="/api/v1")
    application.include_router(version_router, prefix="/api/v1")

    return application


app = create_app()
