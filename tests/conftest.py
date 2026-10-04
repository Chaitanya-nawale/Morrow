"""Pytest configuration and shared fixtures for test suite."""

from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.main import app
from core.config.settings import Settings
from core.types.base import DatabaseStatus


@pytest.fixture
def test_settings() -> Settings:
    """Fixture providing isolated test settings."""
    return Settings(
        app_name="Morrow-Test",
        app_env="testing",
        app_version="0.1.0-test",
        debug=True,
        database_url="postgresql+asyncpg://postgres:postgres@localhost:5432/morrow_test",
        log_level="DEBUG",
    )


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture providing an async HTTP client connected to the FastAPI ASGI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def mock_db_connected() -> Generator[AsyncMock, None, None]:
    """Mock database check returning CONNECTED."""
    with patch("apps.api.routes.health.check_db_connection", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = DatabaseStatus.CONNECTED
        yield mock_check


@pytest.fixture
def mock_db_disconnected() -> Generator[AsyncMock, None, None]:
    """Mock database check returning DISCONNECTED."""
    with patch("apps.api.routes.health.check_db_connection", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = DatabaseStatus.DISCONNECTED
        yield mock_check
