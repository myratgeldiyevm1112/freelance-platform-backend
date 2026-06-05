import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text
from unittest.mock import AsyncMock, patch
from app.main import app
from app.api.dependencies.db import get_db
from app.api.dependencies.cache import get_redis
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import User, Job, Proposal, Contract, Review  # noqa

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5433/freelance_test_db"

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"

VALID_USER = {
    "email": "ratelimit@test.com",
    "password": "TestPass123!",
    "full_name": "Rate Limit User",
    "role": "freelancer",
}


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
async def client(db_session):
    async def override_get_db():
        yield db_session

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True

    async def override_get_redis():
        yield mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    # Reset slowapi limiter storage before each test
    app.state.limiter._storage._storage.clear() if hasattr(
        app.state.limiter._storage, "_storage"
    ) else None

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Forwarded-For": "192.168.1.1"},
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ──────────────────────────────────────────────
# Register rate limit: 5/minute
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register_rate_limit_allows_first_requests(client):
    """First 5 requests должны проходить (201 или 400, но не 429)"""
    for i in range(5):
        payload = {**VALID_USER, "email": f"user{i}@test.com"}
        response = await client.post(REGISTER_URL, json=payload)
        assert response.status_code != 429, (
            f"Request {i+1} was rate limited unexpectedly"
        )


@pytest.mark.asyncio
async def test_register_rate_limit_blocks_6th_request(client):
    """6-й запрос должен вернуть 429"""
    for i in range(5):
        payload = {**VALID_USER, "email": f"block{i}@test.com"}
        await client.post(REGISTER_URL, json=payload)

    # 6th request — должен быть заблокирован
    response = await client.post(REGISTER_URL, json={**VALID_USER, "email": "block6@test.com"})
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_register_rate_limit_response_body(client):
    """429 ответ должен содержать понятное сообщение"""
    for i in range(5):
        payload = {**VALID_USER, "email": f"msg{i}@test.com"}
        await client.post(REGISTER_URL, json=payload)

    response = await client.post(REGISTER_URL, json={**VALID_USER, "email": "msg6@test.com"})
    assert response.status_code == 429
    body = response.text.lower()
    # slowapi возвращает "Rate limit exceeded"
    assert "rate" in body or "limit" in body or "too many" in body


# ──────────────────────────────────────────────
# Login rate limit: 10/minute
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_rate_limit_allows_first_requests(client):
    """Первые 10 запросов на login не должны получать 429"""
    payload = {"email": "notexist@test.com", "password": "WrongPass"}
    for i in range(10):
        response = await client.post(LOGIN_URL, json=payload)
        assert response.status_code != 429, (
            f"Login request {i+1} was rate limited unexpectedly"
        )


@pytest.mark.asyncio
async def test_login_rate_limit_blocks_11th_request(client):
    """11-й запрос на login должен вернуть 429"""
    payload = {"email": "notexist@test.com", "password": "WrongPass"}
    for _ in range(10):
        await client.post(LOGIN_URL, json=payload)

    response = await client.post(LOGIN_URL, json=payload)
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_login_rate_limit_response_body(client):
    """429 на login должен содержать понятное сообщение"""
    payload = {"email": "notexist@test.com", "password": "WrongPass"}
    for _ in range(10):
        await client.post(LOGIN_URL, json=payload)

    response = await client.post(LOGIN_URL, json=payload)
    assert response.status_code == 429
    body = response.text.lower()
    assert "rate" in body or "limit" in body or "too many" in body


# ──────────────────────────────────────────────
# Разные IP — лимиты независимы
# ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rate_limit_is_per_ip(db_session):
    """У каждого IP свой независимый rate limit."""

    async def override_get_db():
        yield db_session

    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True

    async def override_get_redis():
        yield mock_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    # Полная очистка MemoryStorage
    storage = app.state.limiter._storage

    if hasattr(storage, "storage"):
        storage.storage.clear()

    if hasattr(storage, "expirations"):
        storage.expirations.clear()

    try:
        # ---------- IP #1 ----------
        async with AsyncClient(
            transport=ASGITransport(
                app=app,
                client=("10.0.0.1", 50000),
            ),
            base_url="http://test",
        ) as client_ip1:

            for i in range(5):
                response = await client_ip1.post(
                    REGISTER_URL,
                    json={
                        **VALID_USER,
                        "email": f"ip1_{i}@test.com",
                    },
                )

                assert response.status_code != 429

            # 6-й запрос должен блокироваться
            response = await client_ip1.post(
                REGISTER_URL,
                json={
                    **VALID_USER,
                    "email": "ip1_limit@test.com",
                },
            )

            assert response.status_code == 429

        # ---------- IP #2 ----------
        async with AsyncClient(
            transport=ASGITransport(
                app=app,
                client=("10.0.0.2", 50001),
            ),
            base_url="http://test",
        ) as client_ip2:

            response = await client_ip2.post(
                REGISTER_URL,
                json={
                    **VALID_USER,
                    "email": "ip2_first@test.com",
                },
            )

            # Новый IP не должен быть заблокирован
            assert response.status_code != 429

    finally:
        app.dependency_overrides.clear()