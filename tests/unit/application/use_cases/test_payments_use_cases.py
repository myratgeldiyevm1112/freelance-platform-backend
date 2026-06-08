import uuid
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from decimal import Decimal

from app.application.use_cases.create_payment import CreatePayment
from app.application.use_cases.refund_payment import RefundPayment
from app.application.use_cases.release_payment import ReleasePayment
from app.domain.entities.contract import ContractEntity
from app.domain.entities.payment import PaymentEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundError, ForbiddenError, ConflictError, ValidationError
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.database.models.contract import ContractStatus
from app.infrastructure.database.models.payment import PaymentStatus


# ─── Helpers ────────────────────────────────────────────────────────────────

def make_client():
    return UserEntity(
        id=uuid.uuid4(), email="client@test.com", full_name="Client",
        role=UserRole.CLIENT, is_active=True, created_at=datetime.now(),
    )


def make_freelancer():
    return UserEntity(
        id=uuid.uuid4(), email="freelancer@test.com", full_name="Freelancer",
        role=UserRole.FREELANCER, is_active=True, created_at=datetime.now(),
    )


def make_contract(client_id, freelancer_id):
    return ContractEntity(
        id=uuid.uuid4(), job_id=uuid.uuid4(), proposal_id=uuid.uuid4(),
        client_id=client_id, freelancer_id=freelancer_id,
        agreed_rate=Decimal("1000"), status=ContractStatus.ACTIVE,
        created_at=datetime.now(),
    )


def make_payment(contract_id, client_id, freelancer_id, status=PaymentStatus.ESCROWED):
    return PaymentEntity(
        id=uuid.uuid4(),
        contract_id=contract_id,
        client_id=client_id,
        freelancer_id=freelancer_id,
        amount=Decimal("1000"),
        platform_fee=Decimal("100"),
        freelancer_amount=Decimal("900"),
        status=status,
        stripe_payment_intent_id="pi_test_123",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


FAKE_INTENT = {"payment_intent_id": "pi_fake", "client_secret": "secret_fake"}


# ─── CreatePayment ───────────────────────────────────────────────────────────

class TestCreatePayment:

    @pytest.mark.asyncio
    async def test_create_payment_success(self):
        client = make_client()
        freelancer = make_freelancer()
        contract = make_contract(client.id, freelancer.id)
        payment = make_payment(contract.id, client.id, freelancer.id)

        payment_repo = AsyncMock()
        contract_repo = AsyncMock()
        contract_repo.get_by_id.return_value = contract
        payment_repo.get_by_contract_id.return_value = None
        payment_repo.create.return_value = payment
        payment_repo.update_status.return_value = payment

        with patch("app.application.use_cases.create_payment.stripe_service") as mock_stripe:
            mock_stripe.create_payment_intent.return_value = FAKE_INTENT
            use_case = CreatePayment(payment_repo, contract_repo)
            result = await use_case.execute(contract.id, client, freelancer.id)

        assert result["payment_id"] == str(payment.id)
        assert result["client_secret"] == "secret_fake"
        assert result["amount"] == 1000.0
        payment_repo.create.assert_called_once()
        payment_repo.update_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_payment_contract_not_found(self):
        client = make_client()
        payment_repo = AsyncMock()
        contract_repo = AsyncMock()
        contract_repo.get_by_id.return_value = None

        use_case = CreatePayment(payment_repo, contract_repo)

        with pytest.raises(NotFoundError):
            await use_case.execute(uuid.uuid4(), client, uuid.uuid4())

    @pytest.mark.asyncio
    async def test_create_payment_forbidden_not_client(self):
        client = make_client()
        other_client = make_client()  # другой клиент
        freelancer = make_freelancer()
        contract = make_contract(other_client.id, freelancer.id)

        payment_repo = AsyncMock()
        contract_repo = AsyncMock()
        contract_repo.get_by_id.return_value = contract

        use_case = CreatePayment(payment_repo, contract_repo)

        with pytest.raises(ForbiddenError):
            await use_case.execute(contract.id, client, freelancer.id)

    @pytest.mark.asyncio
    async def test_create_payment_already_exists(self):
        client = make_client()
        freelancer = make_freelancer()
        contract = make_contract(client.id, freelancer.id)
        existing = make_payment(contract.id, client.id, freelancer.id)

        payment_repo = AsyncMock()
        contract_repo = AsyncMock()
        contract_repo.get_by_id.return_value = contract
        payment_repo.get_by_contract_id.return_value = existing

        use_case = CreatePayment(payment_repo, contract_repo)

        with pytest.raises(ConflictError):
            await use_case.execute(contract.id, client, freelancer.id)

    @pytest.mark.asyncio
    async def test_create_payment_calls_stripe(self):
        client = make_client()
        freelancer = make_freelancer()
        contract = make_contract(client.id, freelancer.id)
        payment = make_payment(contract.id, client.id, freelancer.id)

        payment_repo = AsyncMock()
        contract_repo = AsyncMock()
        contract_repo.get_by_id.return_value = contract
        payment_repo.get_by_contract_id.return_value = None
        payment_repo.create.return_value = payment
        payment_repo.update_status.return_value = payment

        with patch("app.application.use_cases.create_payment.stripe_service") as mock_stripe:
            mock_stripe.create_payment_intent.return_value = FAKE_INTENT
            use_case = CreatePayment(payment_repo, contract_repo)
            await use_case.execute(contract.id, client, freelancer.id)

        mock_stripe.create_payment_intent.assert_called_once_with(
            amount=1000.0,
            metadata={"contract_id": str(contract.id)},
        )


# ─── RefundPayment ───────────────────────────────────────────────────────────

class TestRefundPayment:

    @pytest.mark.asyncio
    async def test_refund_payment_success(self):
        client = make_client()
        freelancer = make_freelancer()
        contract_id = uuid.uuid4()
        payment = make_payment(contract_id, client.id, freelancer.id)
        refunded = make_payment(contract_id, client.id, freelancer.id, status=PaymentStatus.REFUNDED)

        payment_repo = AsyncMock()
        payment_repo.get_by_contract_id.return_value = payment
        payment_repo.update_status.return_value = refunded

        with patch("app.application.use_cases.refund_payment.stripe_service") as mock_stripe:
            use_case = RefundPayment(payment_repo)
            result = await use_case.execute(contract_id, client)

        assert result.status == PaymentStatus.REFUNDED
        mock_stripe.refund_payment_intent.assert_called_once_with(payment.stripe_payment_intent_id)
        payment_repo.update_status.assert_called_once_with(payment_id=payment.id, status="refunded")

    @pytest.mark.asyncio
    async def test_refund_payment_not_found(self):
        client = make_client()
        payment_repo = AsyncMock()
        payment_repo.get_by_contract_id.return_value = None

        use_case = RefundPayment(payment_repo)

        with pytest.raises(NotFoundError):
            await use_case.execute(uuid.uuid4(), client)

    @pytest.mark.asyncio
    async def test_refund_payment_forbidden(self):
        client = make_client()
        other_client = make_client()
        freelancer = make_freelancer()
        contract_id = uuid.uuid4()
        payment = make_payment(contract_id, other_client.id, freelancer.id)

        payment_repo = AsyncMock()
        payment_repo.get_by_contract_id.return_value = payment

        use_case = RefundPayment(payment_repo)

        with pytest.raises(ForbiddenError):
            await use_case.execute(contract_id, client)

    @pytest.mark.asyncio
    async def test_refund_payment_not_escrowed(self):
        client = make_client()
        freelancer = make_freelancer()
        contract_id = uuid.uuid4()
        payment = make_payment(contract_id, client.id, freelancer.id, status=PaymentStatus.RELEASED)

        payment_repo = AsyncMock()
        payment_repo.get_by_contract_id.return_value = payment

        use_case = RefundPayment(payment_repo)

        with pytest.raises(ValidationError):
            await use_case.execute(contract_id, client)

    @pytest.mark.asyncio
    async def test_refund_skips_stripe_if_no_intent_id(self):
        client = make_client()
        freelancer = make_freelancer()
        contract_id = uuid.uuid4()
        payment = make_payment(contract_id, client.id, freelancer.id)
        payment.stripe_payment_intent_id = None  # нет intent id
        refunded = make_payment(contract_id, client.id, freelancer.id, status=PaymentStatus.REFUNDED)

        payment_repo = AsyncMock()
        payment_repo.get_by_contract_id.return_value = payment
        payment_repo.update_status.return_value = refunded

        with patch("app.application.use_cases.refund_payment.stripe_service") as mock_stripe:
            use_case = RefundPayment(payment_repo)
            result = await use_case.execute(contract_id, client)

        mock_stripe.refund_payment_intent.assert_not_called()
        assert result.status == PaymentStatus.REFUNDED


# ─── ReleasePayment ──────────────────────────────────────────────────────────

class TestReleasePayment:

    @pytest.mark.asyncio
    async def test_release_payment_success(self):
        client = make_client()
        freelancer = make_freelancer()
        contract_id = uuid.uuid4()
        payment = make_payment(contract_id, client.id, freelancer.id)
        released = make_payment(contract_id, client.id, freelancer.id, status=PaymentStatus.RELEASED)

        payment_repo = AsyncMock()
        payment_repo.get_by_contract_id.return_value = payment
        payment_repo.update_status.return_value = released

        use_case = ReleasePayment(payment_repo)
        result = await use_case.execute(contract_id, client)

        assert result.status == PaymentStatus.RELEASED
        payment_repo.update_status.assert_called_once_with(payment_id=payment.id, status="released")

    @pytest.mark.asyncio
    async def test_release_payment_not_found(self):
        client = make_client()
        payment_repo = AsyncMock()
        payment_repo.get_by_contract_id.return_value = None

        use_case = ReleasePayment(payment_repo)

        with pytest.raises(NotFoundError):
            await use_case.execute(uuid.uuid4(), client)

    @pytest.mark.asyncio
    async def test_release_payment_forbidden(self):
        client = make_client()
        other_client = make_client()
        freelancer = make_freelancer()
        contract_id = uuid.uuid4()
        payment = make_payment(contract_id, other_client.id, freelancer.id)

        payment_repo = AsyncMock()
        payment_repo.get_by_contract_id.return_value = payment

        use_case = ReleasePayment(payment_repo)

        with pytest.raises(ForbiddenError):
            await use_case.execute(contract_id, client)

    @pytest.mark.asyncio
    async def test_release_payment_not_escrowed(self):
        client = make_client()
        freelancer = make_freelancer()
        contract_id = uuid.uuid4()
        payment = make_payment(contract_id, client.id, freelancer.id, status=PaymentStatus.RELEASED)

        payment_repo = AsyncMock()
        payment_repo.get_by_contract_id.return_value = payment

        use_case = ReleasePayment(payment_repo)

        with pytest.raises(ValidationError):
            await use_case.execute(contract_id, client)

    @pytest.mark.asyncio
    async def test_release_payment_already_refunded(self):
        client = make_client()
        freelancer = make_freelancer()
        contract_id = uuid.uuid4()
        payment = make_payment(contract_id, client.id, freelancer.id, status=PaymentStatus.REFUNDED)

        payment_repo = AsyncMock()
        payment_repo.get_by_contract_id.return_value = payment

        use_case = ReleasePayment(payment_repo)

        with pytest.raises(ValidationError):
            await use_case.execute(contract_id, client)
