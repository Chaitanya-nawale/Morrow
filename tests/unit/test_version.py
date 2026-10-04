"""Unit tests for the GET /version endpoint."""

import pytest
from httpx import AsyncClient

from core.config.settings import get_settings


@pytest.mark.asyncio
async def test_version_endpoint(async_client: AsyncClient) -> None:
    """Test version endpoint returns 200 and matches current application settings."""
    settings = get_settings()
    response = await async_client.get("/version")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == settings.app_name
    assert data["version"] == settings.app_version
    assert data["tagline"] == settings.app_tagline
    assert data["environment"] == settings.app_env


@pytest.mark.asyncio
async def test_version_endpoint_v1_alias(async_client: AsyncClient) -> None:
    """Test that /api/v1/version alias returns identical metadata."""
    response = await async_client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json()["name"] == "Morrow"
