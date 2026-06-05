# tests/test_upload.py
import pytest
from unittest.mock import patch
from io import BytesIO


async def register_and_login(client, email, role):
    await client.post("/api/v1/auth/register", json={
        "email": email, "password": "password123",
        "full_name": "Test User", "role": role,
    })
    r = await client.post("/api/v1/auth/login", json={
        "email": email, "password": "password123",
    })
    return r.json()["access_token"]


# --- Avatar ---

@pytest.mark.asyncio
async def test_upload_avatar_success(client):
    token = await register_and_login(client, "user@test.com", "freelancer")

    fake_url = "http://localhost:9000/freelance-platform/uuid_avatar.jpg"

    with patch("app.application.use_cases.upload_avatar.s3_service.upload_file", return_value=fake_url):
        response = await client.post(
            "/api/v1/users/me/avatar",
            headers={"authorization": f"Bearer {token}"},
            files={"file": ("avatar.jpg", BytesIO(b"fake_image_data"), "image/jpeg")},
        )

    assert response.status_code == 200
    assert response.json()["avatar_url"] == fake_url


@pytest.mark.asyncio
async def test_upload_avatar_invalid_type(client):
    token = await register_and_login(client, "user@test.com", "freelancer")

    with patch("app.application.use_cases.upload_avatar.s3_service.upload_file"):
        response = await client.post(
            "/api/v1/users/me/avatar",
            headers={"authorization": f"Bearer {token}"},
            files={"file": ("doc.pdf", BytesIO(b"fake_pdf_data"), "application/pdf")},
        )

    assert response.status_code == 400
    assert "JPG" in response.json()["detail"] or "PNG" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_avatar_too_large(client):
    token = await register_and_login(client, "user@test.com", "freelancer")

    big_file = b"x" * (5 * 1024 * 1024 + 1)  # 5MB + 1 byte

    with patch("app.application.use_cases.upload_avatar.s3_service.upload_file"):
        response = await client.post(
            "/api/v1/users/me/avatar",
            headers={"authorization": f"Bearer {token}"},
            files={"file": ("big.jpg", BytesIO(big_file), "image/jpeg")},
        )

    assert response.status_code == 400
    assert "5MB" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_avatar_unauthorized(client):
    response = await client.post(
        "/api/v1/users/me/avatar",
        files={"file": ("avatar.jpg", BytesIO(b"data"), "image/jpeg")},
    )
    assert response.status_code == 401


# --- Portfolio ---

@pytest.mark.asyncio
async def test_upload_portfolio_success(client):
    token = await register_and_login(client, "user@test.com", "freelancer")

    fake_urls = [
        "http://localhost:9000/freelance-platform/uuid1_work.jpg",
        "http://localhost:9000/freelance-platform/uuid2_resume.pdf",
    ]

    with patch(
        "app.application.use_cases.upload_portfolio.s3_service.upload_file",
        side_effect=fake_urls,
    ):
        response = await client.post(
            "/api/v1/users/me/portfolio",
            headers={"authorization": f"Bearer {token}"},
            files=[
                ("files", ("work.jpg", BytesIO(b"img_data"), "image/jpeg")),
                ("files", ("resume.pdf", BytesIO(b"pdf_data"), "application/pdf")),
            ],
        )

    assert response.status_code == 200
    data = response.json()["portfolio_urls"]
    assert len(data) == 2
    assert fake_urls[0] in data
    assert fake_urls[1] in data


@pytest.mark.asyncio
async def test_upload_portfolio_invalid_type(client):
    token = await register_and_login(client, "user@test.com", "freelancer")

    with patch("app.application.use_cases.upload_portfolio.s3_service.upload_file"):
        response = await client.post(
            "/api/v1/users/me/portfolio",
            headers={"authorization": f"Bearer {token}"},
            files=[("files", ("malware.exe", BytesIO(b"bad_data"), "application/octet-stream"))],
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_portfolio_accumulates(client):
    """Повторная загрузка добавляет файлы к существующим."""
    token = await register_and_login(client, "user@test.com", "freelancer")

    url1 = "http://localhost:9000/freelance-platform/uuid1_first.jpg"
    url2 = "http://localhost:9000/freelance-platform/uuid2_second.jpg"

    with patch(
        "app.application.use_cases.upload_portfolio.s3_service.upload_file",
        return_value=url1,
    ):
        await client.post(
            "/api/v1/users/me/portfolio",
            headers={"authorization": f"Bearer {token}"},
            files=[("files", ("first.jpg", BytesIO(b"data"), "image/jpeg"))],
        )

    with patch(
        "app.application.use_cases.upload_portfolio.s3_service.upload_file",
        return_value=url2,
    ):
        response = await client.post(
            "/api/v1/users/me/portfolio",
            headers={"authorization": f"Bearer {token}"},
            files=[("files", ("second.jpg", BytesIO(b"data"), "image/jpeg"))],
        )

    urls = response.json()["portfolio_urls"]
    assert url1 in urls
    assert url2 in urls
    assert len(urls) == 2
