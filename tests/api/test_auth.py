import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "client"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "client"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "client"
    }
    await client.post("/api/v1/auth/register", json=payload)
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "client"
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "client"
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client):
    await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User",
        "role": "client"
    })
    login = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    refresh_token = login.json()["refresh_token"]
    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_logout_success(client):
    # Регистрируемся и логинимся, чтобы получить реальный refresh_token
    await client.post("/api/v1/auth/register", json={
        "email": "logout_test@example.com",
        "password": "password123",
        "full_name": "Logout User",
        "role": "client"
    })
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "logout_test@example.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]

    # Делаем логаут
    response = await client.post("/api/v1/auth/logout", json={
        "refresh_token": refresh_token
    })
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_logout_invalid_token_suppressed(client):
    response = await client.post("/api/v1/auth/logout", json={
        "refresh_token": "completely_invalid_token_garbage"
    })
    
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_refresh_token_after_logout_returns_401(client):
    await client.post("/api/v1/auth/register", json={
        "email": "security_test@example.com",
        "password": "password123",
        "full_name": "Security User",
        "role": "client"
    })
    login_response = await client.post("/api/v1/auth/login", json={
        "email": "security_test@example.com",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]

    await client.post("/api/v1/auth/logout", json={
        "refresh_token": refresh_token
    })

    response = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 401