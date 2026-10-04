"""Unit tests for the GET /health endpoint."""

import pytest
from httpx import AsyncClient

from core.types.base import DatabaseStatus


@pytest.mark.asyncio
async def test_health_endpoint_healthy(
    async_client: AsyncClient, mock_db_connected: object
) -> None:
    """Test health endpoint returns 200 and healthy status when database is connected."""
    response = await async_client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == DatabaseStatus.CONNECTED.value
    assert "timestamp" in data
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_health_endpoint_database_disconnected(
    async_client: AsyncClient, mock_db_disconnected: object
) -> None:
    """Test health endpoint returns 200 and indicates disconnected DB when database check fails."""
    response = await async_client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == DatabaseStatus.DISCONNECTED.value
    assert data["details"] == "Database connection is unavailable."


@pytest.mark.asyncio
async def test_health_endpoint_v1_alias(
    async_client: AsyncClient, mock_db_connected: object
) -> None:
    """Test that /api/v1/health alias returns identical status."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
