import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.api.routers import auth, accounts, transfers, transactions, cards, statements, account_holders, health
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
app.include_router(account_holders.router)
app.include_router(health.router)

from fastapi.responses import JSONResponse
from app.core.error_tracking import get_request_id, new_error_id

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    request_id = get_request_id(request)
    error_id = new_error_id()
    
    logger.exception(f"Unhandled exception", extra={
        "error_id": error_id, 
        "request_id": request_id, 
        "path": request.url.path, 
        "method": request.method
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "error_id": error_id,
            "request_id": request_id
        },
        headers={"X-Request-ID": request_id}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    request_id = get_request_id(request)
    
    if exc.status_code >= 500:
        error_id = new_error_id()
        logger.error(f"HTTPException {exc.status_code}: {exc.detail}", extra={
            "error_id": error_id, 
            "request_id": request_id,
            "path": request.url.path, 
            "method": request.method
        })
        content = {"detail": exc.detail, "error_id": error_id, "request_id": request_id}
    else:
        logger.warning(f"HTTPException {exc.status_code}: {exc.detail}", extra={
            "request_id": request_id,
            "path": request.url.path, 
            "method": request.method
        })
        content = {"detail": exc.detail, "request_id": request_id}
        
    # Extract headers and inject X-Request-ID
    headers = getattr(exc, "headers", None) or {}
    headers["X-Request-ID"] = request_id
        
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=headers
    )

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Banking REST Service API",
        "docs_url": "/docs",
        "live_check": "/live",
        "ready_check": "/ready"
    }
