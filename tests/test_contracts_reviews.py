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


async def setup_contract(client):
    """Создаёт клиента, фрилансера, job, proposal, принимает proposal → возвращает contract_id"""
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")

    job = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test desc", "budget": 500},
        headers={"authorization": f"Bearer {client_token}"}
    )
    job_id = job.json()["id"]

    proposal = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can do this", "proposed_rate": 100},
        headers={"authorization": f"Bearer {freelancer_token}"}
    )
    proposal_id = proposal.json()["id"]

    await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {client_token}"}
    )

    contracts = await client.get(
        "/api/v1/contracts/by-proposal/" + proposal_id,
        headers={"authorization": f"Bearer {client_token}"}
    )

    # получаем contract через БД-независимый способ — ищем через proposal
    # но у нас нет такого эндпоинта, поэтому получим через get proposals и найдём contract
    # временное решение: принимаем proposal и берём contract_id из ответа если он там есть
    # пока используем proposal_id для поиска

    return client_token, freelancer_token, proposal_id


async def get_contract_id(client, token, proposal_id):
    """Хак: ищем контракт через proposal_id напрямую"""
    # У нас нет эндпоинта get contract by proposal,
    # поэтому добавим вспомогательный запрос через proposals
    response = await client.get(
        f"/api/v1/proposals/{proposal_id}/contract",
        headers={"authorization": f"Bearer {token}"}
    )
    return response.json().get("id")


# --- Contract tests ---

@pytest.mark.asyncio
async def test_complete_contract(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")

    job = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test description", "budget": 500},
        headers={"authorization": f"Bearer {client_token}"}
    )
    job_id = job.json()["id"]

    proposal = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can do this", "proposed_rate": 100},
        headers={"authorization": f"Bearer {freelancer_token}"}
    )
    proposal_id = proposal.json()["id"]

    accept = await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {client_token}"}
    )
    assert accept.status_code == 200

    # Получаем contract_id — нужен эндпоинт, пока скипаем
    # TODO: добавить GET /contracts?proposal_id= или вернуть contract в ответе accept


@pytest.mark.asyncio
async def test_complete_contract_wrong_user(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")
    other_token = await register_and_login(client, "other@test.com", "client")

    job = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test description", "budget": 500},
        headers={"authorization": f"Bearer {client_token}"}
    )
    job_id = job.json()["id"]

    proposal = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can do this", "proposed_rate": 100},
        headers={"authorization": f"Bearer {freelancer_token}"}
    )
    proposal_id = proposal.json()["id"]

    await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {client_token}"}
    )

    # other user не может менять статус контракта — но нам нужен contract_id
    # TODO: после фикса эндпоинта


# --- Review tests ---

@pytest.mark.asyncio
async def test_leave_review_success(client):
    client_token = await register_and_login(client, "client@test.com", "client")
    freelancer_token = await register_and_login(client, "freelancer@test.com", "freelancer")

    job = await client.post(
        "/api/v1/jobs/",
        json={"title": "Test Job", "description": "Test description", "budget": 500},
        headers={"authorization": f"Bearer {client_token}"}
    )
    job_id = job.json()["id"]

    proposal = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can do this", "proposed_rate": 100},
        headers={"authorization": f"Bearer {freelancer_token}"}
    )
    proposal_id = proposal.json()["id"]

    await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {client_token}"}
    )

    # TODO: нужен contract_id — сейчас это главная проблема


@pytest.mark.asyncio
async def test_leave_review_on_active_contract_fails(client):
    """Нельзя оставить отзыв на активный контракт"""
    pass  # TODO


@pytest.mark.asyncio
async def test_duplicate_review_fails(client):
    """Нельзя оставить два отзыва на один контракт"""
    pass  # TODO


@pytest.mark.asyncio
async def test_get_user_rating(client):
    """Проверяем агрегацию рейтинга"""
    pass  # TODO
