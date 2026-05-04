"""Health check and error metrics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text

from cartsnitch_api.auth.dependencies import verify_service_key
from cartsnitch_api.cache import get_redis
from cartsnitch_api.database import get_engine
from cartsnitch_api.middleware.error_handler import get_error_monitor

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    engine = get_engine()
    db_ok = False
    redis_ok = False

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    try:
        r = get_redis()
        if r:
            await r.ping()
            redis_ok = True
    except Exception:
        pass

    status = "ok" if db_ok else "degraded"
    return {"status": status, "db": db_ok, "redis": redis_ok}


@router.get("/internal/error-stats", dependencies=[Depends(verify_service_key)])
async def error_stats():
    """Error monitoring stats — internal only (requires X-Service-Key)."""
    monitor = get_error_monitor()
    return monitor.get_stats()
