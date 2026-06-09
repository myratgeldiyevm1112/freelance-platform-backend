import pytest
from tests.api.conftest import register_and_login


async def setup_completed_contract(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")

    job = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test description for job", "budget": 500},
        headers={"authorization": f"Bearer {client_token}"}
    )
    job_id = job.json()["id"]

    proposal = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can do this job well", "proposed_rate": 100},
        headers={"authorization": f"Bearer {freelancer_token}"}
    )
    proposal_id = proposal.json()["id"]

    accept = await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {client_token}"}
    )
    contract_id = accept.json()["contract_id"]

    await client.patch(
        f"/api/v1/contracts/{contract_id}/status",
        json={"new_status": "completed"},
        headers={"authorization": f"Bearer {client_token}"}
    )

    return client_token, freelancer_token, contract_id


@pytest.mark.asyncio
async def test_freelancer_can_also_leave_review(client):
    client_token, freelancer_token, contract_id = await setup_completed_contract(client)

    # клиент оставляет отзыв
    await client.post(
        "/api/v1/reviews/",
        json={"contract_id": contract_id, "rating": 5, "comment": "Great!"},
        headers={"authorization": f"Bearer {client_token}"}
    )

    # получаем client_id
    me = await client.get("/api/v1/users/me", headers={"authorization": f"Bearer {client_token}"})
    client_id = me.json()["id"]

    # проверяем отзыв о клиенте от фрилансера
    response = await client.get(
        f"/api/v1/reviews/user/{client_id}",
        headers={"authorization": f"Bearer {freelancer_token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_rating_no_reviews(client):
    token = await register_and_login(client, "client@test.com", "client")
    me = await client.get("/api/v1/users/me", headers={"authorization": f"Bearer {token}"})
    user_id = me.json()["id"]

    response = await client.get(
        f"/api/v1/reviews/user/{user_id}/rating",
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["average_rating"] == 0.0
    assert response.json()["total_reviews"] == 0


@pytest.mark.asyncio
async def test_cancel_contract(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")

    job = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test description for job", "budget": 500},
        headers={"authorization": f"Bearer {client_token}"}
    )
    job_id = job.json()["id"]

    proposal = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can do this job well", "proposed_rate": 100},
        headers={"authorization": f"Bearer {freelancer_token}"}
    )
    proposal_id = proposal.json()["id"]

    accept = await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {client_token}"}
    )
    contract_id = accept.json()["contract_id"]

    response = await client.patch(
        f"/api/v1/contracts/{contract_id}/status",
        json={"new_status": "cancelled"},
        headers={"authorization": f"Bearer {client_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
