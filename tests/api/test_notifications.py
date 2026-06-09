import pytest
from unittest.mock import AsyncMock, patch
from tests.api.conftest import register_and_login


async def get_user_id(client, token):
    r = await client.get("/api/v1/users/me", headers={"authorization": f"Bearer {token}"})
    return r.json()["id"]


async def create_notification(client, client_token, freelancer_token):
    """Создаём уведомление через submit proposal."""
    r = await client.post("/api/v1/jobs/", json={
        "title": "Notif Test Job", "description": "Test job", "budget": "500.00"
    }, headers={"authorization": f"Bearer {client_token}"})
    job_id = r.json()["id"]

    with patch("app.infrastructure.websocket.manager.manager.send_to_user", new_callable=AsyncMock):
        await client.post(
            f"/api/v1/proposals/jobs/{job_id}/proposals",
            json={"cover_letter": "I can do this", "proposed_rate": "100.00"},
            headers={"authorization": f"Bearer {freelancer_token}"},
        )


# ═══════════════════════════════════════════
# Get notifications
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_get_notifications_empty(client):
    token = await register_and_login(client, "notif_empty@test.com", "client")
    r = await client.get("/api/v1/notifications/", headers={"authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_get_notifications_after_proposal(client):
    client_token = await register_and_login(client, "notif_client@test.com", "client")
    freelancer_token = await register_and_login(client, "notif_freelancer@test.com", "freelancer")

    await create_notification(client, client_token, freelancer_token)

    r = await client.get("/api/v1/notifications/", headers={"authorization": f"Bearer {client_token}"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert data[0]["type"] == "proposal_submitted"
    assert data[0]["is_read"] is False


# ═══════════════════════════════════════════
# Unread count
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_unread_count_increases(client):
    client_token = await register_and_login(client, "notif_count@test.com", "client")
    freelancer_token = await register_and_login(client, "notif_count_f@test.com", "freelancer")

    r = await client.get("/api/v1/notifications/unread", headers={"authorization": f"Bearer {client_token}"})
    assert r.json()["unread_count"] == 0

    await create_notification(client, client_token, freelancer_token)

    r = await client.get("/api/v1/notifications/unread", headers={"authorization": f"Bearer {client_token}"})
    assert r.json()["unread_count"] == 1


# ═══════════════════════════════════════════
# Mark as read
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_mark_notification_as_read(client):
    client_token = await register_and_login(client, "notif_read@test.com", "client")
    freelancer_token = await register_and_login(client, "notif_read_f@test.com", "freelancer")

    await create_notification(client, client_token, freelancer_token)

    r = await client.get("/api/v1/notifications/", headers={"authorization": f"Bearer {client_token}"})
    notification_id = r.json()[0]["id"]

    r = await client.patch(
        f"/api/v1/notifications/{notification_id}/read",
        headers={"authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200
    assert r.json()["is_read"] is True


# ═══════════════════════════════════════════
# Mark all as read
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_mark_all_notifications_as_read(client):
    client_token = await register_and_login(client, "notif_all@test.com", "client")
    freelancer_token = await register_and_login(client, "notif_all_f@test.com", "freelancer")

    await create_notification(client, client_token, freelancer_token)

    r = await client.patch("/api/v1/notifications/read-all", headers={"authorization": f"Bearer {client_token}"})
    assert r.status_code == 200

    r = await client.get("/api/v1/notifications/unread", headers={"authorization": f"Bearer {client_token}"})
    assert r.json()["unread_count"] == 0


# ═══════════════════════════════════════════
# Auth check
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_notifications_unauthorized(client):
    r = await client.get("/api/v1/notifications/")
    assert r.status_code == 401
