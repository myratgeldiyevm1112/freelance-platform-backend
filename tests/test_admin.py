import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import select
from app.infrastructure.database.models.user import User


async def register_and_login(client, email, role):
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "password123",
        "full_name": "Test User", "role": role,
    })
    r = await client.post("/api/v1/auth/login", json={
        "email": email, "password": "password123",
    })
    return r.json()["access_token"]


async def get_user_id(client, token):
    r = await client.get("/api/v1/users/me", headers={"authorization": f"Bearer {token}"})
    return r.json()["id"]


async def make_admin(db_session, user_id):
    """Напрямую в БД ставим is_admin=True."""
    result = await db_session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one()
    user.is_admin = True
    await db_session.commit()


# ═══════════════════════════════════════════
# Admin access control
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_admin_endpoint_forbidden_for_regular_user(client):
    token = await register_and_login(client, "admin_regular@test.com", "client")
    r = await client.get("/api/v1/admin/users", headers={"authorization": f"Bearer {token}"})
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_admin_endpoint_unauthorized(client):
    r = await client.get("/api/v1/admin/users")
    assert r.status_code == 401


# ═══════════════════════════════════════════
# Admin users
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_admin_get_users(client, db_session):
    token = await register_and_login(client, "admin_user@test.com", "client")
    user_id = await get_user_id(client, token)
    await make_admin(db_session, user_id)

    r = await client.get("/api/v1/admin/users", headers={"authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) >= 1


@pytest.mark.asyncio
async def test_admin_ban_user(client, db_session):
    admin_token = await register_and_login(client, "admin_ban@test.com", "client")
    admin_id = await get_user_id(client, admin_token)
    await make_admin(db_session, admin_id)

    target_token = await register_and_login(client, "admin_ban_target@test.com", "freelancer")
    target_id = await get_user_id(client, target_token)

    r = await client.patch(
        f"/api/v1/admin/users/{target_id}/ban",
        headers={"authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["is_active"] is False


@pytest.mark.asyncio
async def test_admin_unban_user(client, db_session):
    admin_token = await register_and_login(client, "admin_unban@test.com", "client")
    admin_id = await get_user_id(client, admin_token)
    await make_admin(db_session, admin_id)

    target_token = await register_and_login(client, "admin_unban_target@test.com", "freelancer")
    target_id = await get_user_id(client, target_token)

    await client.patch(
        f"/api/v1/admin/users/{target_id}/ban",
        headers={"authorization": f"Bearer {admin_token}"},
    )
    r = await client.patch(
        f"/api/v1/admin/users/{target_id}/unban",
        headers={"authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 200
    assert r.json()["is_active"] is True


# ═══════════════════════════════════════════
# Admin jobs
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_admin_get_jobs(client, db_session):
    admin_token = await register_and_login(client, "admin_jobs@test.com", "client")
    admin_id = await get_user_id(client, admin_token)
    await make_admin(db_session, admin_id)

    await client.post("/api/v1/jobs/", json={
        "title": "Admin Test Job", "description": "Test description", "budget": "500.00"
    }, headers={"authorization": f"Bearer {admin_token}"})

    r = await client.get("/api/v1/admin/jobs", headers={"authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


@pytest.mark.asyncio
async def test_admin_delete_job(client, db_session):
    admin_token = await register_and_login(client, "admin_del@test.com", "client")
    admin_id = await get_user_id(client, admin_token)
    await make_admin(db_session, admin_id)

    job_r = await client.post("/api/v1/jobs/", json={
        "title": "Job to delete", "description": "Test description", "budget": "500.00"
    }, headers={"authorization": f"Bearer {admin_token}"})
    job_id = job_r.json()["id"]

    r = await client.delete(
        f"/api/v1/admin/jobs/{job_id}",
        headers={"authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 204


# ═══════════════════════════════════════════
# Admin stats
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_admin_get_stats(client, db_session):
    admin_token = await register_and_login(client, "admin_stats@test.com", "client")
    admin_id = await get_user_id(client, admin_token)
    await make_admin(db_session, admin_id)

    r = await client.get("/api/v1/admin/stats", headers={"authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    data = r.json()
    assert "total_users" in data
    assert "total_jobs" in data
    assert "total_contracts" in data
    assert "total_platform_revenue" in data
    assert "open_disputes" in data
