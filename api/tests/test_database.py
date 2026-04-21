"""Tests for database initialization and lifecycle."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cartsnitch_api.database import (
    close_db,
    create_db_engine,
    get_engine,
    init_db,
)


@pytest.mark.asyncio
async def test_create_db_engine_creates_engine_with_pool_settings():
    """Test that create_db_engine creates engine with correct pool settings."""
    engine = create_db_engine()
    assert engine is not None
    pool = engine.pool
    assert pool.size() == 10
    assert pool._max_overflow == 20
    await engine.dispose()


@pytest.mark.asyncio
async def test_init_db_sets_engine_and_factory():
    """Test that init_db properly initializes the engine and session factory."""
    await init_db()
    try:
        eng = get_engine()
        assert eng is not None
        from cartsnitch_api import database

        assert database.async_session_factory is not None
    finally:
        await close_db()


@pytest.mark.asyncio
async def test_close_db_disposes_engine():
    """Test that close_db properly disposes the engine."""
    await init_db()
    await close_db()
    assert get_engine() is None
    from cartsnitch_api import database

    assert database.async_session_factory is None


@pytest.mark.asyncio
async def test_get_db_yields_session_after_init():
    """Test that get_db yields working sessions after init_db."""
    await init_db()
    try:
        from cartsnitch_api.database import get_db

        gen = get_db()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        await gen.aclose()
    finally:
        await close_db()
