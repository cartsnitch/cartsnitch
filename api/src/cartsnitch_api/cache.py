"""Redis/DragonflyDB caching helpers."""

import redis.asyncio as redis

from cartsnitch_api.config import settings


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


cache_client = CacheClient()
