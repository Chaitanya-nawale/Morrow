"""Integration tests for FastAPI application lifecycle and endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_openapi_schema(async_client: AsyncClient) -> None:
    """Verify that OpenAPI schema is properly generated."""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data
    assert "/health" in data["paths"]
    assert "/version" in data["paths"]


@pytest.mark.asyncio
async def test_not_found_endpoint(async_client: AsyncClient) -> None:
    """Verify standard 404 response for nonexistent routes."""
    response = await async_client.get("/nonexistent-endpoint")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cors_headers(async_client: AsyncClient) -> None:
    """Verify CORS preflight headers."""
    response = await async_client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in {200, 204}
    assert "access-control-allow-origin" in response.headers
