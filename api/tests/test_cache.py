"""Tests for Redis/DragonflyDB caching lifecycle."""

import pytest

from cartsnitch_api.cache import CacheClient, close_redis, get_redis, init_redis


@pytest.mark.asyncio
async def test_init_redis_creates_client():
    """Test that init_redis creates the Redis client."""
    await init_redis()
    try:
        r = get_redis()
        assert r is not None
        await r.ping()
    finally:
        await close_redis()


@pytest.mark.asyncio
async def test_close_redis_clears_client():
    """Test that close_redis properly closes and clears the client."""
    await init_redis()
    await close_redis()
    assert get_redis() is None


@pytest.mark.asyncio
async def test_cache_client_get_returns_none_when_not_connected():
    """Test that CacheClient.get returns None gracefully when Redis is down."""
    client = CacheClient()
    # Without init_redis, get should return None
    result = await client.get("test-key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_client_set_does_not_raise_when_not_connected():
    """Test that CacheClient.set does not raise when Redis is down."""
    client = CacheClient()
    # Without init_redis, set should not raise
    await client.set("test-key", "test-value", ttl_seconds=60)


@pytest.mark.asyncio
async def test_cache_client_delete_does_not_raise_when_not_connected():
    """Test that CacheClient.delete does not raise when Redis is down."""
    client = CacheClient()
    # Without init_redis, delete should not raise
    await client.delete("test-key")
