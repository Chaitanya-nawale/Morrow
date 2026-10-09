"""Pytest configuration and shared fixtures for test suite."""

import os
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from apps.api.main import app
from core.config.settings import Settings
from core.types.base import DatabaseStatus
from db.models import SQLModel

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/morrow_test",
)


@pytest.fixture
def test_settings() -> Settings:
    """Fixture providing isolated test settings."""
    return Settings(
        app_name="Morrow-Test",
        app_env="testing",
        app_version="0.1.0-test",
        debug=True,
        database_url=TEST_DB_URL,
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


@pytest.fixture
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Provide an async database engine for testing with schema initialization."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session rolled back after each test."""
    session_factory = async_sessionmaker(
        bind=db_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()
        await session.close()
