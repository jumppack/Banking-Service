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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all domain routers
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transfers.router)
app.include_router(transactions.router)
app.include_router(cards.router)
app.include_router(statements.router)

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
