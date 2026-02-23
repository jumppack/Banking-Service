import logging
from fastapi import FastAPI
from app.api.routers import auth, accounts, transfers, transactions, cards, statements

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Banking REST Service", description="A production-ready Banking API")

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
async def health_check():
    return {"status": "healthy"}
