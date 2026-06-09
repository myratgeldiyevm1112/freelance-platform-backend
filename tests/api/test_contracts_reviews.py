import pytest
import uuid
from tests.api.conftest import register_and_login

async def create_active_contract(client):
    """Вспомогательный метод: создает контракт чисто через API и возвращает токены и contract_id."""
    client_token = await register_and_login(client, f"client_{uuid.uuid4()}@test.com", "client")
    freelancer_token = await register_and_login(client, f"free_{uuid.uuid4()}@test.com", "freelancer")

    job = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test description", "budget": 500},
        headers={"authorization": f"Bearer {client_token}"}
    )
    job_id = job.json()["id"]

    proposal = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "Men 3yyl islap yorun node bn", "proposed_rate": 150},
        headers={"authorization": f"Bearer {freelancer_token}"}
    )
    proposal_id = proposal.json()["id"]

    accept_response = await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {client_token}"}
    )
    
    contract_id = accept_response.json()["contract_id"]
    
    return client_token, freelancer_token, contract_id


# ═══════════════════════════════════════════
# Contract Tests
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_complete_contract(client):
    client_token, _, contract_id = await create_active_contract(client)

    response = await client.patch(
        f"/api/v1/contracts/{contract_id}/status",
        json={"new_status": "completed"},
        headers={"authorization": f"Bearer {client_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_complete_contract_wrong_user(client):
    _, _, contract_id = await create_active_contract(client)
    
    other_token = await register_and_login(client, f"intruder_{uuid.uuid4()}@test.com", "client")
    
    response = await client.patch(
        f"/api/v1/contracts/{contract_id}/status",
        json={"new_status": "completed"},
        headers={"authorization": f"Bearer {other_token}"}
    )
    assert response.status_code in [403, 404]


# ═══════════════════════════════════════════
# Review Tests
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_leave_review_success(client):
    client_token, _, contract_id = await create_active_contract(client)

    await client.patch(
        f"/api/v1/contracts/{contract_id}/status",
        json={"new_status": "completed"},
        headers={"authorization": f"Bearer {client_token}"}
    )

    response = await client.post(
        "/api/v1/reviews/",
        json={
            "contract_id": contract_id,
            "rating": 5,
            "comment": "Gowy isledi, nody gowy bilyar eken!"
        },
        headers={"authorization": f"Bearer {client_token}"}
    )
    assert response.status_code == 201
    assert response.json()["rating"] == 5


@pytest.mark.asyncio
async def test_leave_review_on_active_contract_fails(client):
    client_token, _, contract_id = await create_active_contract(client)

    response = await client.post(
        "/api/v1/reviews/",
        json={
            "contract_id": contract_id,
            "rating": 4,
            "comment": "Contract is not finished yet"
        },
        headers={"authorization": f"Bearer {client_token}"}
    )
    assert response.status_code == 400 


@pytest.mark.asyncio
async def test_duplicate_review_fails(client):
    client_token, _, contract_id = await create_active_contract(client)

    await client.patch(
        f"/api/v1/contracts/{contract_id}/status",
        json={"new_status": "completed"},
        headers={"authorization": f"Bearer {client_token}"}
    )

    payload = {"contract_id": contract_id, "rating": 5, "comment": "Excellent"}
    
    r1 = await client.post("/api/v1/reviews/", json=payload, headers={"authorization": f"Bearer {client_token}"})
    assert r1.status_code == 201

    r2 = await client.post("/api/v1/reviews/", json=payload, headers={"authorization": f"Bearer {client_token}"})
    assert r2.status_code in [400, 409]