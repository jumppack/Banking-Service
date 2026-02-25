import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api.routers import auth, accounts, transfers, transactions, cards, statements
from app.db.session import engine, get_db
from app.core.logging import setup_logging

# Configure structural JSON logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    logger.info("Starting up Banking REST Service")
    yield
    # Shutdown: Clean up resources
    logger.info("Shutting down Banking REST Service")
    await engine.dispose()

app = FastAPI(
    title="Banking REST Service",
    description="A production-ready Banking API",
    lifespan=lifespan
)

# Configure CORS for Frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost",
        "http://127.0.0.1"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.middleware.logging_middleware import LoggingMiddleware
app.add_middleware(LoggingMiddleware)

# Include all domain routers
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transfers.router)
app.include_router(transactions.router)
app.include_router(cards.router)
app.include_router(statements.router)

from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    if exc.status_code >= 500:
        logger.error(f"HTTPException {exc.status_code}: {exc.detail}")
    else:
        logger.warning(f"HTTPException {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=getattr(exc, "headers", None)
    )

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Banking REST Service API",
        "docs_url": "/docs",
        "health_check": "/health"
    }

@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_db)):
    try:
        # Perform a deep health check by querying the database
        await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is unhealthy or database is unreachable"
        )
