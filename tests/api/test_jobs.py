import pytest
from tests.api.conftest import register_and_login


@pytest.mark.asyncio
async def test_create_job_as_client(client):
    token = await register_and_login(client, "client@test.com", "client")
    response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test desc", "budget": 500},
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Job"
    assert data["status"] == "open"


@pytest.mark.asyncio
async def test_create_job_as_freelancer_forbidden(client):
    token = await register_and_login(client, "freelancer@test.com", "freelancer")
    response = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test desc", "budget": 500},
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_jobs(client):
    token = await register_and_login(client, "client@test.com", "client")
    await client.post(
        "/api/v1/jobs/",
        json={"title": "Job 1", "description": "Desc 1", "budget": 500},
        headers={"authorization": f"Bearer {token}"}
    )
    response = await client.get("/api/v1/jobs/", headers={"authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 1


@pytest.mark.asyncio
async def test_get_jobs_filter_by_status(client):
    token = await register_and_login(client, "client@test.com", "client")
    await client.post(
        "/api/v1/jobs/",
        json={"title": "Job 1", "description": "Desc 1", "budget": 500},
        headers={"authorization": f"Bearer {token}"}
    )
    response = await client.get("/api/v1/jobs/?status=open", headers={"authorization": f"Bearer {token}"})
    assert response.status_code == 200
    for job in response.json()["items"]:
        assert job["status"] == "open"


@pytest.mark.asyncio
async def test_get_job_by_id(client):
    token = await register_and_login(client, "client@test.com", "client")
    created = await client.post(
        "/api/v1/jobs/",
        json={"title": "Job 1", "description": "Desc 1", "budget": 500},
        headers={"authorization": f"Bearer {token}"}
    )
    job_id = created.json()["id"]
    response = await client.get(f"/api/v1/jobs/{job_id}", headers={"authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == job_id


@pytest.mark.asyncio
async def test_get_job_not_found(client):
    token = await register_and_login(client, "client@test.com", "client")
    response = await client.get(
        "/api/v1/jobs/00000000-0000-0000-0000-000000000000",
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404