# tests/test_websocket.py
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.db import get_db
from app.api.dependencies.cache import get_redis


# --- Хелперы ---

async def register_and_login(client, email, role):
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "password123",
        "full_name": "Test User", "role": role,
    })
    r = await client.post("/api/v1/auth/login", json={
        "email": email, "password": "password123",
    })
    return r.json()["access_token"]


async def get_user_id(client, token):
    r = await client.get(
        "/api/v1/users/me",
        headers={"authorization": f"Bearer {token}"},
    )
    return r.json()["id"]


async def create_job(client, token):
    r = await client.post(
        "/api/v1/jobs/",
        json={"title": "WS Test Job", "description": "Test description", "budget": "500.00"},
        headers={"authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201, f"create_job failed: {r.json()}"
    return r.json()["id"]


TEST_DB_URL = "postgresql+asyncpg://postgres:password@localhost:5433/freelance_test_db"


def make_ws_client(db_session=None):
    """TestClient для WS — использует переданную сессию или создаёт новую."""
    if db_session is None:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
        _engine = create_async_engine(TEST_DB_URL)
        _maker = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)

        async def override_db():
            async with _maker() as s:
                yield s
    else:
        async def override_db():
            yield db_session

    store = {}
    redis_mock = AsyncMock()

    async def fake_set(key, value, *args, **kwargs):
        store[key] = value

    async def fake_get(key):
        return store.get(key)

    async def fake_delete(*keys):
        for k in keys:
            store.pop(k, None)

    redis_mock.set = fake_set
    redis_mock.get = fake_get
    redis_mock.delete = fake_delete

    async def override_redis():
        yield redis_mock

    # Сохраняем текущие overrides чтобы не затирать
    saved = dict(app.dependency_overrides)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = override_redis
    client = TestClient(app, raise_server_exceptions=False)
    # Восстанавливаем
    app.dependency_overrides.clear()
    app.dependency_overrides.update(saved)
    return client


# ═══════════════════════════════════════════
# Тесты подключения (WS handshake)
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_ws_connect_valid_token(client):
    """Успешное подключение с валидным токеном."""
    token = await register_and_login(client, "wsuser@test.com", "client")
    user_id = await get_user_id(client, token)

    ws_client = make_ws_client()
    with ws_client.websocket_connect(f"/api/v1/ws/{user_id}?token={token}") as ws:
        ws.close()


@pytest.mark.asyncio
async def test_ws_connect_invalid_token(client):
    """Отклонение при невалидном токене."""
    token = await register_and_login(client, "wsuser@test.com", "client")
    user_id = await get_user_id(client, token)

    ws_client = make_ws_client()
    with pytest.raises(Exception):
        with ws_client.websocket_connect(f"/api/v1/ws/{user_id}?token=bad.token.here"):
            pass


@pytest.mark.asyncio
async def test_ws_connect_wrong_user_id(client):
    """Отклонение если token.sub != user_id в пути."""
    token_a = await register_and_login(client, "userA@test.com", "client")
    token_b = await register_and_login(client, "userB@test.com", "client")
    user_id_b = await get_user_id(client, token_b)

    ws_client = make_ws_client()
    with pytest.raises(Exception):
        with ws_client.websocket_connect(f"/api/v1/ws/{user_id_b}?token={token_a}"):
            pass


# ═══════════════════════════════════════════
# Тесты событий (мокаем manager)
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_ws_receives_proposal_submitted(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    client_user_id = await get_user_id(client, client_token)
    job_id = await create_job(client, client_token)

    with patch(
        "app.infrastructure.websocket.manager.manager.send_to_user",
        new_callable=AsyncMock,
    ) as mock_send:
        resp = await client.post(
            f"/api/v1/proposals/jobs/{job_id}/proposals",
            json={"cover_letter": "I can do this", "proposed_rate": "100.00"},
            headers={"authorization": f"Bearer {freelancer_token}"},
        )
        assert resp.status_code == 201
        mock_send.assert_awaited_once()

        args   = mock_send.call_args.args
        kwargs = mock_send.call_args.kwargs

        # user_id всегда positional
        assert args[0] == client_user_id
        # event и data могут быть positional или keyword
        event = args[1] if len(args) > 1 else kwargs["event"]
        data  = args[2] if len(args) > 2 else kwargs["data"]

        assert event == "proposal_submitted"
        assert data["job_id"] == job_id
        assert "freelancer_name" in data
        assert "proposal_id" in data


@pytest.mark.asyncio
async def test_ws_receives_proposal_accepted(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    freelancer_user_id = await get_user_id(client, freelancer_token)
    job_id = await create_job(client, client_token)

    proposal_resp = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can do this", "proposed_rate": "100.00"},
        headers={"authorization": f"Bearer {freelancer_token}"},
    )
    assert proposal_resp.status_code == 201
    proposal_id = proposal_resp.json()["id"]

    with patch(
        "app.infrastructure.websocket.manager.manager.send_to_user",
        new_callable=AsyncMock,
    ) as mock_send:
        resp = await client.patch(
            f"/api/v1/proposals/{proposal_id}",
            json={"status": "accepted"},
            headers={"authorization": f"Bearer {client_token}"},
        )
        assert resp.status_code == 200
        mock_send.assert_awaited_once()

        args   = mock_send.call_args.args
        kwargs = mock_send.call_args.kwargs

        assert args[0] == freelancer_user_id
        event = args[1] if len(args) > 1 else kwargs["event"]
        data  = args[2] if len(args) > 2 else kwargs["data"]

        assert event == "proposal_accepted"
        assert data["job_id"] == job_id
        assert "contract_id" in data
        assert "client_name" in data

@pytest.mark.asyncio
async def test_ws_no_event_if_not_connected(client):
    """Если юзер офлайн — proposal подаётся без ошибок (500)."""
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    job_id = await create_job(client, client_token)

    r = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can do this", "proposed_rate": "100.00"},
        headers={"authorization": f"Bearer {freelancer_token}"},
    )
    assert r.status_code == 201

# ═══════════════════════════════════════════
# Юнит-тесты ConnectionManager
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_manager_is_connected():
    from app.infrastructure.websocket.manager import ConnectionManager
    from unittest.mock import AsyncMock

    m = ConnectionManager()
    ws = AsyncMock()
    assert m.is_connected("user1") is False
    await m.connect("user1", ws)
    assert m.is_connected("user1") is True
    m.disconnect("user1", ws)
    assert m.is_connected("user1") is False


@pytest.mark.asyncio
async def test_manager_send_to_user_dead_socket():
    from app.infrastructure.websocket.manager import ConnectionManager
    from unittest.mock import AsyncMock

    m = ConnectionManager()
    ws = AsyncMock()
    ws.send_json = AsyncMock(side_effect=Exception("connection closed"))

    await m.connect("user1", ws)
    # dead socket — не должен падать
    await m.send_to_user("user1", "test_event", {"key": "value"})
    # после отправки dead socket должен быть удалён
    assert m.is_connected("user1") is False
