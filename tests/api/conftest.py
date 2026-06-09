# tests/api/conftest.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.api.dependencies.db import get_db
from app.api.dependencies.cache import get_redis
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import User, Job, Proposal, Contract, Review  # noqa

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5433/freelance_test_db"

@pytest_asyncio.fixture(scope="function")
async def engine():
    _engine = create_async_engine(TEST_DATABASE_URL)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    await _engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def mock_redis():
    """Мок Redis с реальным хранилищем в памяти для API-тестов."""
    store = {}
    redis = AsyncMock()

    async def fake_set(key, value, *args, **kwargs):
        store[key] = value
        return True

    async def fake_get(key):
        return store.get(key)

    async def fake_delete(*keys):
        for key in keys:
            store.pop(key, None)
        return len(keys)

    redis.set = fake_set
    redis.get = fake_get
    redis.delete = fake_delete
    return redis

@pytest_asyncio.fixture(scope="function")
async def client(db_session, mock_redis):
    async def override_get_db():
        yield db_session

    async def override_get_redis():
        yield mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

async def register_and_login(client, email: str, role: str) -> str:
    await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "password123",
        "full_name": "Test User",
        "role": role
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "password123"
    })
    return response.json()["access_token"]