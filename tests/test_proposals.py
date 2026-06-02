import pytest


async def register_and_login(client, email, role):
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


async def create_job(client, token):
    response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test desc", "budget": 500},
        headers={"authorization": f"Bearer {token}"}
    )
    return response.json()["id"]


async def submit_proposal(client, token, job_id):
    response = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can do this", "proposed_rate": 100},
        headers={"authorization": f"Bearer {token}"}
    )
    return response


# --- Submit proposal ---

@pytest.mark.asyncio
async def test_submit_proposal_as_freelancer(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    job_id = await create_job(client, client_token)

    response = await submit_proposal(client, freelancer_token, job_id)
    assert response.status_code == 201
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_submit_proposal_as_client_forbidden(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    job_id = await create_job(client, client_token)

    response = await submit_proposal(client, client_token, job_id)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_submit_duplicate_proposal(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    job_id = await create_job(client, client_token)

    await submit_proposal(client, freelancer_token, job_id)
    response = await submit_proposal(client, freelancer_token, job_id)
    assert response.status_code == 400


# --- List proposals ---

@pytest.mark.asyncio
async def test_list_proposals_as_client(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    job_id = await create_job(client, client_token)
    await submit_proposal(client, freelancer_token, job_id)

    response = await client.get(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        headers={"authorization": f"Bearer {client_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_list_proposals_as_freelancer_forbidden(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    job_id = await create_job(client, client_token)

    response = await client.get(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        headers={"authorization": f"Bearer {freelancer_token}"}
    )
    assert response.status_code == 403


# --- Accept / Reject proposal ---

@pytest.mark.asyncio
async def test_accept_proposal_creates_contract(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    job_id = await create_job(client, client_token)
    proposal = await submit_proposal(client, freelancer_token, job_id)
    proposal_id = proposal.json()["id"]

    response = await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {client_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_reject_proposal(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    job_id = await create_job(client, client_token)
    proposal = await submit_proposal(client, freelancer_token, job_id)
    proposal_id = proposal.json()["id"]

    response = await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "rejected"},
        headers={"authorization": f"Bearer {client_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_accept_proposal_as_freelancer_forbidden(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    job_id = await create_job(client, client_token)
    proposal = await submit_proposal(client, freelancer_token, job_id)
    proposal_id = proposal.json()["id"]

    response = await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {freelancer_token}"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_accept_already_accepted_proposal(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    job_id = await create_job(client, client_token)
    proposal = await submit_proposal(client, freelancer_token, job_id)
    proposal_id = proposal.json()["id"]

    await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {client_token}"}
    )
    response = await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "rejected"},
        headers={"authorization": f"Bearer {client_token}"}
    )
    assert response.status_code == 400
