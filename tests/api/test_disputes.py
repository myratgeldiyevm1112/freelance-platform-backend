import pytest
from unittest.mock import AsyncMock, patch
from tests.api.conftest import register_and_login


async def get_user_id(client, token):
    r = await client.get("/api/v1/users/me", headers={"authorization": f"Bearer {token}"})
    return r.json()["id"]


async def create_contract(client, client_token, freelancer_token):
    job_r = await client.post("/api/v1/jobs/", json={
        "title": "Dispute Test Job", "description": "Test description", "budget": "1000.00"
    }, headers={"authorization": f"Bearer {client_token}"})
    job_id = job_r.json()["id"]

    with patch("app.infrastructure.websocket.manager.manager.send_to_user", new_callable=AsyncMock):
        proposal_r = await client.post(
            f"/api/v1/proposals/jobs/{job_id}/proposals",
            json={"cover_letter": "I can do this", "proposed_rate": "1000.00"},
            headers={"authorization": f"Bearer {freelancer_token}"},
        )
        proposal_id = proposal_r.json()["id"]

        accept_r = await client.patch(
            f"/api/v1/proposals/{proposal_id}",
            json={"status": "accepted"},
            headers={"authorization": f"Bearer {client_token}"},
        )
    return accept_r.json()["contract_id"]


# ═══════════════════════════════════════════
# Open dispute
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_open_dispute_success(client):
    client_token = await register_and_login(client, "disp_client@test.com", "client")
    freelancer_token = await register_and_login(client, "disp_freelancer@test.com", "freelancer")
    contract_id = await create_contract(client, client_token, freelancer_token)

    r = await client.post("/api/v1/disputes/", json={
        "contract_id": contract_id,
        "reason": "Freelancer did not deliver the work as agreed",
    }, headers={"authorization": f"Bearer {client_token}"})

    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "open"
    assert data["contract_id"] == contract_id


@pytest.mark.asyncio
async def test_open_dispute_duplicate(client):
    client_token = await register_and_login(client, "disp_dup_client@test.com", "client")
    freelancer_token = await register_and_login(client, "disp_dup_freelancer@test.com", "freelancer")
    contract_id = await create_contract(client, client_token, freelancer_token)

    await client.post("/api/v1/disputes/", json={
        "contract_id": contract_id,
        "reason": "Freelancer did not deliver the work as agreed",
    }, headers={"authorization": f"Bearer {client_token}"})

    r = await client.post("/api/v1/disputes/", json={
        "contract_id": contract_id,
        "reason": "Another dispute attempt",
    }, headers={"authorization": f"Bearer {client_token}"})

    assert r.status_code == 409


@pytest.mark.asyncio
async def test_open_dispute_not_participant(client):
    client_token = await register_and_login(client, "disp_np_client@test.com", "client")
    freelancer_token = await register_and_login(client, "disp_np_freelancer@test.com", "freelancer")
    other_token = await register_and_login(client, "disp_np_other@test.com", "client")
    contract_id = await create_contract(client, client_token, freelancer_token)

    r = await client.post("/api/v1/disputes/", json={
        "contract_id": contract_id,
        "reason": "I want to dispute this contract",
    }, headers={"authorization": f"Bearer {other_token}"})

    assert r.status_code == 403


@pytest.mark.asyncio
async def test_open_dispute_unauthorized(client):
    r = await client.post("/api/v1/disputes/", json={
        "contract_id": "00000000-0000-0000-0000-000000000000",
        "reason": "Some reason here",
    })
    assert r.status_code == 401


# ═══════════════════════════════════════════
# Admin — get all disputes
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_get_all_disputes(client):
    client_token = await register_and_login(client, "disp_admin_client@test.com", "client")
    freelancer_token = await register_and_login(client, "disp_admin_fl@test.com", "freelancer")
    contract_id = await create_contract(client, client_token, freelancer_token)

    await client.post("/api/v1/disputes/", json={
        "contract_id": contract_id,
        "reason": "Work was not completed properly",
    }, headers={"authorization": f"Bearer {client_token}"})

    r = await client.get("/api/v1/disputes/admin", headers={"authorization": f"Bearer {client_token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


# ═══════════════════════════════════════════
# Resolve dispute
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_resolve_dispute_non_admin(client):
    client_token = await register_and_login(client, "disp_res_client@test.com", "client")
    freelancer_token = await register_and_login(client, "disp_res_fl@test.com", "freelancer")
    contract_id = await create_contract(client, client_token, freelancer_token)

    r = await client.post("/api/v1/disputes/", json={
        "contract_id": contract_id,
        "reason": "Work was not completed properly",
    }, headers={"authorization": f"Bearer {client_token}"})
    dispute_id = r.json()["id"]

    r = await client.patch(f"/api/v1/disputes/{dispute_id}/resolve", json={
        "resolution": "refund",
        "resolution_note": "Client is right",
    }, headers={"authorization": f"Bearer {client_token}"})

    assert r.status_code == 403
