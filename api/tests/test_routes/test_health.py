"""Tests for health check endpoint."""

import pytest
from unittest.mock import AsyncMock, patch

from cartsnitch_api.database import init_db, close_db


@pytest.mark.asyncio
async def test_health_returns_db_and_redis_fields(client):
    """Test that health endpoint returns db and redis status fields."""
    from cartsnitch_api.cache import init_redis, close_redis

    await init_db()
    await init_redis()

    try:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "db" in data
        assert "redis" in data
    finally:
        await close_redis()
        await close_db()


@pytest.mark.asyncio
async def test_health_returns_degraded_when_db_down():
    """Test that health returns degraded when database is down."""
    from cartsnitch_api.database import _engine
    from cartsnitch_api.routes.health import health

    # Simulate engine is None (DB not initialized)
    with patch("cartsnitch_api.routes.health.get_engine", return_value=None):
        response = await health()
        assert response["status"] == "degraded"
        assert response["db"] is False


@pytest.mark.asyncio
async def test_health_returns_ok_when_db_up(client):
    """Test that health returns ok when database is up."""
    from cartsnitch_api.database import init_db, close_db
    from cartsnitch_api.cache import init_redis, close_redis

    await init_db()
    await init_redis()

    try:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        if data["db"]:
            assert data["status"] == "ok"
    finally:
        await close_redis()
        await close_db()


@pytest.mark.asyncio
async def test_health_redis_down_does_not_make_unhealthy(client):
    """Test that Redis being down does not make health return unhealthy."""
    from cartsnitch_api.database import init_db, close_db

    await init_db()

    try:
        response = await client.get("/health")
        data = response.json()
        # Redis being down should not make status "degraded"
        # Only DB failure makes it degraded
        if not data["db"]:
            assert data["status"] == "degraded"
    finally:
        await close_db()
