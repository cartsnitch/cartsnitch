"""Redis/DragonflyDB caching helpers."""

import logging
from typing import TYPE_CHECKING

import redis.asyncio as redis
from redis.asyncio import Redis

from cartsnitch_api.config import settings

if TYPE_CHECKING:
    from cartsnitch_api.config import Settings

logger = logging.getLogger(__name__)

_redis: "Redis | None" = None


def get_settings() -> "Settings":
    return settings


async def init_redis() -> None:
    global _redis
    _redis = redis.from_url(settings.redis_url)
    await _redis.ping()


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


def get_redis() -> Redis | None:
    return _redis


class CacheClient:
    """Redis/DragonflyDB caching with connection pooling.

    Will be used for expensive queries: price trends, product comparisons.
    Cache invalidation via Redis pub/sub events from other services.
    """

    def __init__(self) -> None:
        self._pool: redis.ConnectionPool | None = None
        self._client: redis.Redis | None = None

    async def initialize(self) -> None:
        """Initialize the Redis connection pool."""
        self._pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=20,
            decode_responses=True,
        )
        self._client = redis.Redis(connection_pool=self._pool)

    async def close(self) -> None:
        """Close the Redis connection pool."""
        if self._client:
            await self._client.aclose()
        if self._pool:
            await self._pool.aclose()

    async def get(self, key: str) -> str | None:
        if not self._client:
            return None
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl_seconds: int = 300) -> None:
        if not self._client:
            return
        await self._client.set(key, value, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        if not self._client:
            return
        await self._client.delete(key)

    async def invalidate_price_cache(self, product_id: str) -> None:
        """Invalidate all price-related cache entries for a product."""
        if not self._client:
            return
        pattern = f"price:*:{product_id}"
        await self._delete_pattern(pattern)

    async def invalidate_product_cache(self, product_id: str) -> None:
        """Invalidate the product detail cache entry."""
        if not self._client:
            return
        await self._client.delete(f"product:{product_id}")

    async def _delete_pattern(self, pattern: str) -> None:
        """Delete all keys matching a pattern using SCAN."""
        if not self._client:
            return
        cursor = 0
        while True:
            cursor, keys = await self._client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self._client.delete(*keys)
            if cursor == 0:
                break


cache_client = CacheClient()
