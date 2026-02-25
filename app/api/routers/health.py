from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])

@router.get("/live", summary="Liveness Probe", description="Always returns 200 OK to indicate the API process is running.")
async def liveness_probe():
    return {"status": "ok"}

@router.get("/ready", summary="Readiness Probe", description="Checks database connectivity and Alembic migrations.")
async def readiness_probe(session: AsyncSession = Depends(get_db)):
    try:
        # 1. Check basic DB connection
        await session.execute(text("SELECT 1"))
        
        # 2. Check Alembic migrations
        table_check = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'"))
        if not table_check.scalar_one_or_none():
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "not_ready", "detail": "Alembic version table missing"}
            )
            
        version_check = await session.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
        if not version_check.scalar_one_or_none():
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "not_ready", "detail": "Alembic migrations not applied"}
            )
            
        return {"status": "ready"}
        
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "detail": "Service is unhealthy or database is unreachable"}
        )

# Alias for backwards compatibility
@router.get("/health", summary="Health Check (Legacy)", description="Legacy alias for /ready.")
async def health_check(session: AsyncSession = Depends(get_db)):
    return await readiness_probe(session)
