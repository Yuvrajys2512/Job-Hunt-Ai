"""
Health check endpoints.

These are critical in production:
- Load balancers ping /health every few seconds to decide if this instance
  is alive. If it returns non-200, traffic is routed elsewhere.
- The /health/detailed endpoint lets you know if the DB and Redis are
  reachable — so you know if a partial failure is happening.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """Simple liveness check — returns 200 if the process is running."""
    return {"status": "ok", "service": "jobhunt-ai-api"}


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness check — verifies DB connectivity.
    Returns 200 only if all critical dependencies are reachable.

    Depends(get_db) is FastAPI's dependency injection.
    FastAPI sees this parameter, calls get_db(), and passes the result in.
    You never call get_db() yourself — FastAPI handles it.
    """
    checks = {}

    # Test DB connection
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    all_ok = all(v == "ok" for v in checks.values())

    return {
        "status": "ok" if all_ok else "degraded",
        "checks": checks,
    }
