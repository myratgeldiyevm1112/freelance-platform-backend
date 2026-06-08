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


# --- Skills endpoints ---

@pytest.mark.asyncio
async def test_add_skills(client):
    token = await register_and_login(client, "freelancer_skills@test.com", "freelancer")
    response = await client.post(
        "/api/v1/users/me/skills",
        json={"skills": ["python", "fastapi", "postgresql"]},
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["skills"]) == 3
    skill_names = [s["skill_name"] for s in data["skills"]]
    assert "python" in skill_names
    assert "fastapi" in skill_names


@pytest.mark.asyncio
async def test_add_skills_normalized(client):
    token = await register_and_login(client, "freelancer_norm@test.com", "freelancer")
    response = await client.post(
        "/api/v1/users/me/skills",
        json={"skills": ["Python", "  FASTAPI  ", "Django"]},
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    skill_names = [s["skill_name"] for s in response.json()["skills"]]
    assert "python" in skill_names
    assert "fastapi" in skill_names
    assert "django" in skill_names


@pytest.mark.asyncio
async def test_add_skills_no_duplicates(client):
    token = await register_and_login(client, "freelancer_dup@test.com", "freelancer")
    await client.post(
        "/api/v1/users/me/skills",
        json={"skills": ["python"]},
        headers={"authorization": f"Bearer {token}"}
    )
    # добавляем тот же скилл снова
    response = await client.post(
        "/api/v1/users/me/skills",
        json={"skills": ["python"]},
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()["skills"]) == 0  # дубликат не добавился


@pytest.mark.asyncio
async def test_get_skills(client):
    token = await register_and_login(client, "freelancer_get@test.com", "freelancer")
    await client.post(
        "/api/v1/users/me/skills",
        json={"skills": ["python", "django"]},
        headers={"authorization": f"Bearer {token}"}
    )
    response = await client.get(
        "/api/v1/users/me/skills",
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    skill_names = [s["skill_name"] for s in response.json()["skills"]]
    assert "python" in skill_names
    assert "django" in skill_names


@pytest.mark.asyncio
async def test_get_skills_empty(client):
    token = await register_and_login(client, "freelancer_empty@test.com", "freelancer")
    response = await client.get(
        "/api/v1/users/me/skills",
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["skills"] == []


# --- Job filtering ---

@pytest.mark.asyncio
async def test_create_job_with_skills(client):
    token = await register_and_login(client, "client_skills@test.com", "client")
    response = await client.post(
        "/api/v1/jobs/",
        json={
            "title": "Python Developer",
            "description": "Need a Python expert",
            "budget": 1000,
            "required_skills": ["python", "fastapi"]
        },
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["required_skills"] == ["python", "fastapi"]


@pytest.mark.asyncio
async def test_filter_jobs_by_skill(client):
    token = await register_and_login(client, "client_filter@test.com", "client")
    await client.post(
        "/api/v1/jobs/",
        json={
            "title": "Python Developer",
            "description": "Need a Python expert",
            "budget": 1000,
            "required_skills": ["python", "fastapi"]
        },
        headers={"authorization": f"Bearer {token}"}
    )
    await client.post(
        "/api/v1/jobs/",
        json={
            "title": "Java Developer",
            "description": "Need a Java expert",
            "budget": 1500,
            "required_skills": ["java", "spring"]
        },
        headers={"authorization": f"Bearer {token}"}
    )
    response = await client.get(
        "/api/v1/jobs/?skill=python",
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) >= 1
    for job in items:
        assert "python" in job["required_skills"]


@pytest.mark.asyncio
async def test_fulltext_search_jobs(client):
    token = await register_and_login(client, "client_search@test.com", "client")
    await client.post(
        "/api/v1/jobs/",
        json={
            "title": "Django Backend Developer",
            "description": "We need an experienced Django developer",
            "budget": 2000,
            "required_skills": ["django", "python"]
        },
        headers={"authorization": f"Bearer {token}"}
    )
    response = await client.get(
        "/api/v1/jobs/?q=django",
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) >= 1
    titles = [job["title"] for job in items]
    assert any("Django" in t for t in titles)


@pytest.mark.asyncio
async def test_fulltext_search_no_results(client):
    token = await register_and_login(client, "client_nosearch@test.com", "client")
    response = await client.get(
        "/api/v1/jobs/?q=xyznonexistentterm123",
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0

@pytest.mark.asyncio
async def test_remove_skill(client):
    token = await register_and_login(client, "freelancer_del@test.com", "freelancer")
    add_response = await client.post(
        "/api/v1/users/me/skills",
        json={"skills": ["python"]},
        headers={"authorization": f"Bearer {token}"}
    )
    skill_id = add_response.json()["skills"][0]["id"]

    response = await client.delete(
        f"/api/v1/users/me/skills/{skill_id}",
        headers={"authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    skill_id = add_response.json()["skills"][0]["skill_id"]