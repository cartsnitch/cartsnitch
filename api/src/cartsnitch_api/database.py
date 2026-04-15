"""Database session management for the API gateway."""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cartsnitch_api.config import settings

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


_engine: "Engine | None" = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


def create_db_engine():
    return create_async_engine(
        settings.database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )


async def init_db() -> None:
    global _engine, async_session_factory
    _engine = create_db_engine()
    async_session_factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)


async def close_db() -> None:
    global _engine, async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
    async_session_factory = None


def get_engine():
    return _engine


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with async_session_factory() as session:
        yield session


# Backward compatibility: module-level engine proxy that delegates to _engine
def __getattr__(name: str):
    if name == "engine":
        if _engine is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")
        return _engine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
