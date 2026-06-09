import pytest
from unittest.mock import patch
from tests.api.conftest import register_and_login


async def get_user_id(client, token):
    r = await client.get("/api/v1/users/me", headers={"authorization": f"Bearer {token}"})
    return r.json()["id"]


async def create_contract(client, client_token, freelancer_token):
    """Создаём контракт через полный flow: job → proposal → accept."""
    freelancer_id = await get_user_id(client, freelancer_token)

    job_r = await client.post(
        "/api/v1/jobs/",
        json={"title": "Payment Test Job", "description": "Test description", "budget": "1000.00"},
        headers={"authorization": f"Bearer {client_token}"},
    )
    job_id = job_r.json()["id"]

    proposal_r = await client.post(
        f"/api/v1/proposals/jobs/{job_id}/proposals",
        json={"cover_letter": "I can do this", "proposed_rate": "1000.00"},
        headers={"authorization": f"Bearer {freelancer_token}"},
    )
    proposal_id = proposal_r.json()["id"]

    accept_r = await client.patch(
        f"/api/v1/proposals/{proposal_id}",
        json={"status": "accepted"},
        headers={"authorization": f"Bearer {client_token}"},
    )
    contract_id = accept_r.json()["contract_id"]
    return contract_id, freelancer_id


FAKE_INTENT = {
    "payment_intent_id": "pi_test_123",
    "client_secret": "pi_test_123_secret_abc",
    "status": "requires_payment_method",
}


# ═══════════════════════════════════════════
# Create payment
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_create_payment_success(client):
    client_token = await register_and_login(client, "pay_client@test.com", "client")
    freelancer_token = await register_and_login(client, "pay_freelancer@test.com", "freelancer")
    contract_id, freelancer_id = await create_contract(client, client_token, freelancer_token)

    with patch("app.infrastructure.payment.stripe_service.stripe.PaymentIntent.create", return_value=type("obj", (object,), {
        "id": "pi_test_123",
        "client_secret": "pi_test_123_secret_abc",
        "status": "requires_payment_method",
    })()):
        r = await client.post(
            f"/api/v1/payments/contracts/{contract_id}",
            json={"freelancer_id": freelancer_id},
            headers={"authorization": f"Bearer {client_token}"},
        )

    assert r.status_code == 201
    data = r.json()
    assert "client_secret" in data
    assert data["amount"] == 1000.0
    assert data["platform_fee"] == 100.0
    assert data["freelancer_amount"] == 900.0


@pytest.mark.asyncio
async def test_create_payment_duplicate(client):
    client_token = await register_and_login(client, "pay_client2@test.com", "client")
    freelancer_token = await register_and_login(client, "pay_freelancer2@test.com", "freelancer")
    contract_id, freelancer_id = await create_contract(client, client_token, freelancer_token)

    with patch("app.infrastructure.payment.stripe_service.stripe.PaymentIntent.create", return_value=type("obj", (object,), {
        "id": "pi_test_123",
        "client_secret": "pi_test_123_secret_abc",
        "status": "requires_payment_method",
    })()):
        await client.post(
            f"/api/v1/payments/contracts/{contract_id}",
            json={"freelancer_id": freelancer_id},
            headers={"authorization": f"Bearer {client_token}"},
        )
        r = await client.post(
            f"/api/v1/payments/contracts/{contract_id}",
            json={"freelancer_id": freelancer_id},
            headers={"authorization": f"Bearer {client_token}"},
        )

    assert r.status_code == 409


@pytest.mark.asyncio
async def test_create_payment_forbidden(client):
    client_token = await register_and_login(client, "pay_client3@test.com", "client")
    freelancer_token = await register_and_login(client, "pay_freelancer3@test.com", "freelancer")
    contract_id, freelancer_id = await create_contract(client, client_token, freelancer_token)

    with patch("app.infrastructure.payment.stripe_service.stripe.PaymentIntent.create", return_value=type("obj", (object,), {
        "id": "pi_test_123",
        "client_secret": "secret",
        "status": "requires_payment_method",
    })()):
        r = await client.post(
            f"/api/v1/payments/contracts/{contract_id}",
            json={"freelancer_id": freelancer_id},
            headers={"authorization": f"Bearer {freelancer_token}"},
        )

    assert r.status_code == 403


@pytest.mark.asyncio
async def test_create_payment_contract_not_found(client):
    client_token = await register_and_login(client, "pay_404@test.com", "client")
    fake_contract_id = "00000000-0000-0000-0000-000000000000"

    r = await client.post(
        f"/api/v1/payments/contracts/{fake_contract_id}",
        json={"freelancer_id": "00000000-0000-0000-0000-000000000001"},
        headers={"authorization": f"Bearer {client_token}"},
    )

    assert r.status_code == 404

# ═══════════════════════════════════════════
# Release payment
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_release_payment_success(client):
    client_token = await register_and_login(client, "pay_client4@test.com", "client")
    freelancer_token = await register_and_login(client, "pay_freelancer4@test.com", "freelancer")
    contract_id, freelancer_id = await create_contract(client, client_token, freelancer_token)

    with patch("app.infrastructure.payment.stripe_service.stripe.PaymentIntent.create", return_value=type("obj", (object,), {
        "id": "pi_test_456",
        "client_secret": "secret",
        "status": "requires_payment_method",
    })()):
        await client.post(
            f"/api/v1/payments/contracts/{contract_id}",
            json={"freelancer_id": freelancer_id},
            headers={"authorization": f"Bearer {client_token}"},
        )

    r = await client.post(
        f"/api/v1/payments/contracts/{contract_id}/release",
        headers={"authorization": f"Bearer {client_token}"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "released"


# ═══════════════════════════════════════════
# Refund payment
# ═══════════════════════════════════════════

@pytest.mark.asyncio
async def test_refund_payment_success(client):
    client_token = await register_and_login(client, "pay_client5@test.com", "client")
    freelancer_token = await register_and_login(client, "pay_freelancer5@test.com", "freelancer")
    contract_id, freelancer_id = await create_contract(client, client_token, freelancer_token)

    with patch("app.infrastructure.payment.stripe_service.stripe.PaymentIntent.create", return_value=type("obj", (object,), {
        "id": "pi_test_789",
        "client_secret": "secret",
        "status": "requires_payment_method",
    })()):
        await client.post(
            f"/api/v1/payments/contracts/{contract_id}",
            json={"freelancer_id": freelancer_id},
            headers={"authorization": f"Bearer {client_token}"},
        )

    with patch("app.infrastructure.payment.stripe_service.stripe.Refund.create", return_value=type("obj", (object,), {
        "id": "re_test_123",
        "status": "succeeded",
    })()):
        r = await client.post(
            f"/api/v1/payments/contracts/{contract_id}/refund",
            headers={"authorization": f"Bearer {client_token}"},
        )

    assert r.status_code == 200
    assert r.json()["status"] == "refunded"
