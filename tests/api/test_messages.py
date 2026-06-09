import pytest
from unittest.mock import AsyncMock, patch
from tests.api.conftest import register_and_login


async def get_user_id(client, token):
    r = await client.get("/api/v1/users/me", headers={"authorization": f"Bearer {token}"})
    return r.json()["id"]


# ═══════════════════════════════════════════
# Send message
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_send_message_success(client):
    token_a = await register_and_login(client, "sender@test.com", "client")
    token_b = await register_and_login(client, "receiver@test.com", "freelancer")
    user_b_id = await get_user_id(client, token_b)

    with patch("app.infrastructure.websocket.manager.manager.send_to_user", new_callable=AsyncMock):
        r = await client.post(
            "/api/v1/messages/",
            json={"receiver_id": user_b_id, "content": "Hello!"},
            headers={"authorization": f"Bearer {token_a}"},
        )

    assert r.status_code == 201
    data = r.json()
    assert data["content"] == "Hello!"
    assert data["is_read"] is False


@pytest.mark.asyncio
async def test_send_message_to_self(client):
    token = await register_and_login(client, "self@test.com", "client")
    user_id = await get_user_id(client, token)

    with patch("app.infrastructure.websocket.manager.manager.send_to_user", new_callable=AsyncMock):
        r = await client.post(
            "/api/v1/messages/",
            json={"receiver_id": user_id, "content": "Hello me!"},
            headers={"authorization": f"Bearer {token}"},
        )

    assert r.status_code == 400


@pytest.mark.asyncio
async def test_send_message_empty_content(client):
    token_a = await register_and_login(client, "sender2@test.com", "client")
    token_b = await register_and_login(client, "receiver2@test.com", "freelancer")
    user_b_id = await get_user_id(client, token_b)

    with patch("app.infrastructure.websocket.manager.manager.send_to_user", new_callable=AsyncMock):
        r = await client.post(
            "/api/v1/messages/",
            json={"receiver_id": user_b_id, "content": "   "},
            headers={"authorization": f"Bearer {token_a}"},
        )

    assert r.status_code == 422


@pytest.mark.asyncio
async def test_send_message_unauthorized(client):
    r = await client.post(
        "/api/v1/messages/",
        json={"receiver_id": "00000000-0000-0000-0000-000000000000", "content": "Hello"},
    )
    assert r.status_code == 401


# ═══════════════════════════════════════════
# Get conversation
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_get_conversation(client):
    token_a = await register_and_login(client, "chatter_a@test.com", "client")
    token_b = await register_and_login(client, "chatter_b@test.com", "freelancer")
    user_b_id = await get_user_id(client, token_b)
    user_a_id = await get_user_id(client, token_a)

    with patch("app.infrastructure.websocket.manager.manager.send_to_user", new_callable=AsyncMock):
        await client.post(
            "/api/v1/messages/",
            json={"receiver_id": user_b_id, "content": "First message"},
            headers={"authorization": f"Bearer {token_a}"},
        )
        await client.post(
            "/api/v1/messages/",
            json={"receiver_id": user_a_id, "content": "Reply message"},
            headers={"authorization": f"Bearer {token_b}"},
        )

    r = await client.get(
        f"/api/v1/messages/conversations/{user_b_id}",
        headers={"authorization": f"Bearer {token_a}"},
    )
    assert r.status_code == 200
    assert len(r.json()) == 2


# ═══════════════════════════════════════════
# Unread count
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_unread_count(client):
    token_a = await register_and_login(client, "unreader_a@test.com", "client")
    token_b = await register_and_login(client, "unreader_b@test.com", "freelancer")
    user_b_id = await get_user_id(client, token_b)

    with patch("app.infrastructure.websocket.manager.manager.send_to_user", new_callable=AsyncMock):
        await client.post(
            "/api/v1/messages/",
            json={"receiver_id": user_b_id, "content": "Unread msg 1"},
            headers={"authorization": f"Bearer {token_a}"},
        )
        await client.post(
            "/api/v1/messages/",
            json={"receiver_id": user_b_id, "content": "Unread msg 2"},
            headers={"authorization": f"Bearer {token_a}"},
        )

    r = await client.get(
        "/api/v1/messages/unread",
        headers={"authorization": f"Bearer {token_b}"},
    )
    assert r.status_code == 200
    assert r.json()["unread_count"] == 2


# ═══════════════════════════════════════════
# Get conversations list
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_get_conversations_list(client):
    token_a = await register_and_login(client, "conv_a@test.com", "client")
    token_b = await register_and_login(client, "conv_b@test.com", "freelancer")
    user_b_id = await get_user_id(client, token_b)

    with patch("app.infrastructure.websocket.manager.manager.send_to_user", new_callable=AsyncMock):
        await client.post(
            "/api/v1/messages/",
            json={"receiver_id": user_b_id, "content": "Hey!"},
            headers={"authorization": f"Bearer {token_a}"},
        )

    r = await client.get(
        "/api/v1/messages/conversations",
        headers={"authorization": f"Bearer {token_a}"},
    )
    assert r.status_code == 200
    assert len(r.json()) >= 1
    assert r.json()[0]["last_message"] == "Hey!"
