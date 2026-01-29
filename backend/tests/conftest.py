import os

# SQLite in-memory für Tests - MUSS vor App-Imports gesetzt werden
os.environ["CHOREQUEST_DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["CHOREQUEST_API_KEY"] = "test-key"
os.environ["CHOREQUEST_CLAUDE_API_KEY"] = ""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

HEADERS = {"Authorization": "Bearer test-key"}


@pytest.fixture(autouse=True)
async def setup_database():
    """Erstellt alle Tabellen vor jedem Test, löscht sie danach."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Gibt eine Test-DB-Session zurück."""
    async with TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """HTTP-Client für API-Tests mit DB-Override."""
    async def override_get_db():
        async with TestSession() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
