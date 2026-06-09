import pytest
from tests.api.conftest import register_and_login

async def get_user_id(client, token):
    r = await client.get("/api/v1/users/me", headers={"authorization": f"Bearer {token}"})
    return r.json()["id"]


# ═══════════════════════════════════════════
# Search freelancers
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_search_freelancers_empty(client):
    token = await register_and_login(client, "fl_search_client@test.com", "client")
    r = await client.get("/api/v1/freelancers/", headers={"authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)


@pytest.mark.asyncio
async def test_search_freelancers_returns_freelancers(client):
    client_token = await register_and_login(client, "fl_client@test.com", "client")
    freelancer_token = await register_and_login(client, "fl_freelancer@test.com", "freelancer")

    await client.patch("/api/v1/users/me", json={
        "bio": "Python developer", "hourly_rate": 50.0
    }, headers={"authorization": f"Bearer {freelancer_token}"})

    r = await client.get("/api/v1/freelancers/", headers={"authorization": f"Bearer {client_token}"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert any(f["hourly_rate"] == 50.0 for f in data)


@pytest.mark.asyncio
async def test_search_freelancers_filter_by_rate(client):
    client_token = await register_and_login(client, "fl_rate_client@test.com", "client")
    freelancer_token = await register_and_login(client, "fl_rate_f@test.com", "freelancer")

    await client.patch("/api/v1/users/me", json={
        "bio": "Designer", "hourly_rate": 30.0
    }, headers={"authorization": f"Bearer {freelancer_token}"})

    r = await client.get(
        "/api/v1/freelancers/?min_rate=20&max_rate=40",
        headers={"authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert all(f["hourly_rate"] <= 40.0 for f in data if f["hourly_rate"])


@pytest.mark.asyncio
async def test_search_freelancers_filter_by_name(client):
    client_token = await register_and_login(client, "fl_name_client@test.com", "client")
    freelancer_token = await register_and_login(client, "fl_name_f@test.com", "freelancer")

    await client.patch("/api/v1/users/me", json={
        "bio": "Unique bio xyz123"
    }, headers={"authorization": f"Bearer {freelancer_token}"})

    r = await client.get(
        "/api/v1/freelancers/?q=xyz123",
        headers={"authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()) >= 1


@pytest.mark.asyncio
async def test_search_freelancers_by_skill(client):
    client_token = await register_and_login(client, "fl_skill_client@test.com", "client")
    freelancer_token = await register_and_login(client, "fl_skill_f@test.com", "freelancer")

    await client.post("/api/v1/users/me/skills", json={"skills": ["rust"]},
        headers={"authorization": f"Bearer {freelancer_token}"})

    r = await client.get(
        "/api/v1/freelancers/?skill=rust",
        headers={"authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200
    assert len(r.json()) >= 1


# ═══════════════════════════════════════════
# Get freelancer profile
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_get_freelancer_profile(client):
    client_token = await register_and_login(client, "fl_profile_client@test.com", "client")
    freelancer_token = await register_and_login(client, "fl_profile_f@test.com", "freelancer")
    freelancer_id = await get_user_id(client, freelancer_token)

    r = await client.get(
        f"/api/v1/freelancers/{freelancer_id}",
        headers={"authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == freelancer_id


@pytest.mark.asyncio
async def test_get_freelancer_profile_not_found(client):
    token = await register_and_login(client, "fl_nf_client@test.com", "client")
    r = await client.get(
        "/api/v1/freelancers/00000000-0000-0000-0000-000000000000",
        headers={"authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_freelancers_unauthorized(client):
    r = await client.get("/api/v1/freelancers/")
    assert r.status_code == 401
