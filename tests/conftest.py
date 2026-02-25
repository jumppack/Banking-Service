import os
import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Set a fallback SECRET_KEY for testing before importing the app
os.environ.setdefault("SECRET_KEY", "test-secret-key-please-change")

from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Use an in-memory SQLite database for test isolation
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Mock alembic_version table for readiness probes
        from sqlalchemy import text
        await conn.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL, CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num))"))
        await conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('test_version')"))
    yield
    # Drop tables after testing is done
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(session: AsyncSession):
    # Override the app dependency to inject the isolated test session
    async def override_get_db():
        yield session
        
    app.dependency_overrides[get_db] = override_get_db
    
    # We use ASGITransport from httpx for FastAPI 0.112+ async testing
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
        
    # Clear overrides after the test
    app.dependency_overrides.clear()
