import uuid
import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from decimal import Decimal

from app.application.use_cases.resolve_dispute import ResolveDispute, GetDisputes
from app.domain.entities.dispute import DisputeEntity
from app.domain.entities.user import UserEntity
from app.domain.entities.payment import PaymentEntity
from app.domain.exceptions import ForbiddenError, NotFoundError, ValidationError
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.database.models.dispute import DisputeStatus
from app.infrastructure.database.models.contract import ContractStatus


def make_admin():
    u = UserEntity(
        id=uuid.uuid4(), email="admin@test.com", full_name="Admin",
        role=UserRole.CLIENT, is_active=True, created_at=datetime.now(),
    )
    u.is_admin = True
    return u


def make_regular_user():
    u = UserEntity(
        id=uuid.uuid4(), email="user@test.com", full_name="Regular",
        role=UserRole.FREELANCER, is_active=True, created_at=datetime.now(),
    )
    u.is_admin = False
    return u


def make_dispute(status=DisputeStatus.OPEN):
    return DisputeEntity(
        id=uuid.uuid4(),
        contract_id=uuid.uuid4(),
        opened_by=uuid.uuid4(),
        reason="Payment not released",
        status=status,
        resolved_by=None,
        resolution_note=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def make_payment(contract_id):
    return PaymentEntity(
        id=uuid.uuid4(),
        contract_id=contract_id,
        client_id=uuid.uuid4(),
        freelancer_id=uuid.uuid4(),
        amount=Decimal("500"),
        platform_fee=Decimal("25"),
        freelancer_amount=Decimal("475"),
        status="held",
        stripe_payment_intent_id="pi_test",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def make_use_case(dispute_repo, contract_repo, payment_repo):
    return ResolveDispute(
        dispute_repo=dispute_repo,
        contract_repo=contract_repo,
        payment_repo=payment_repo,
    )


# --- Permission check ---

@pytest.mark.asyncio
async def test_non_admin_cannot_resolve_dispute():
    user = make_regular_user()
    use_case = make_use_case(AsyncMock(), AsyncMock(), AsyncMock())

    with pytest.raises(ForbiddenError):
        await use_case.execute(uuid.uuid4(), "refund", None, user)


# --- Not found ---

@pytest.mark.asyncio
async def test_dispute_not_found():
    admin = make_admin()
    dispute_repo = AsyncMock()
    dispute_repo.get_by_id.return_value = None

    use_case = make_use_case(dispute_repo, AsyncMock(), AsyncMock())

    with pytest.raises(NotFoundError):
        await use_case.execute(uuid.uuid4(), "refund", None, admin)


# --- Already resolved ---

@pytest.mark.asyncio
async def test_already_resolved_dispute():
    admin = make_admin()
    dispute = make_dispute(status=DisputeStatus.RESOLVED_REFUND)
    dispute_repo = AsyncMock()
    dispute_repo.get_by_id.return_value = dispute

    use_case = make_use_case(dispute_repo, AsyncMock(), AsyncMock())

    with pytest.raises(ValidationError):
        await use_case.execute(dispute.id, "refund", None, admin)


# --- Invalid resolution ---

@pytest.mark.asyncio
async def test_invalid_resolution_value():
    admin = make_admin()
    dispute = make_dispute()
    dispute_repo = AsyncMock()
    dispute_repo.get_by_id.return_value = dispute

    use_case = make_use_case(dispute_repo, AsyncMock(), AsyncMock())

    with pytest.raises(ValidationError):
        await use_case.execute(dispute.id, "invalid_resolution", None, admin)


# --- Refund path ---

@pytest.mark.asyncio
async def test_resolve_dispute_refund():
    admin = make_admin()
    dispute = make_dispute()
    payment = make_payment(dispute.contract_id)
    resolved = make_dispute(status=DisputeStatus.RESOLVED_REFUND)
    resolved.id = dispute.id

    dispute_repo = AsyncMock()
    dispute_repo.get_by_id.return_value = dispute
    dispute_repo.resolve.return_value = resolved
    contract_repo = AsyncMock()
    payment_repo = AsyncMock()
    payment_repo.get_by_contract_id.return_value = payment

    use_case = make_use_case(dispute_repo, contract_repo, payment_repo)
    result = await use_case.execute(dispute.id, "refund", "Client wins", admin)

    assert result.status == DisputeStatus.RESOLVED_REFUND
    contract_repo.update_status.assert_called_once_with(dispute.contract_id, ContractStatus.CANCELLED)
    payment_repo.update_status.assert_called_once_with(payment.id, "refunded")
    dispute_repo.resolve.assert_called_once_with(
        dispute_id=dispute.id,
        status=DisputeStatus.RESOLVED_REFUND,
        resolved_by=admin.id,
        resolution_note="Client wins",
    )


# --- Release path ---

@pytest.mark.asyncio
async def test_resolve_dispute_release():
    admin = make_admin()
    dispute = make_dispute()
    payment = make_payment(dispute.contract_id)
    resolved = make_dispute(status=DisputeStatus.RESOLVED_RELEASE)
    resolved.id = dispute.id

    dispute_repo = AsyncMock()
    dispute_repo.get_by_id.return_value = dispute
    dispute_repo.resolve.return_value = resolved
    contract_repo = AsyncMock()
    payment_repo = AsyncMock()
    payment_repo.get_by_contract_id.return_value = payment

    use_case = make_use_case(dispute_repo, contract_repo, payment_repo)
    result = await use_case.execute(dispute.id, "release", "Freelancer wins", admin)

    assert result.status == DisputeStatus.RESOLVED_RELEASE
    contract_repo.update_status.assert_called_once_with(dispute.contract_id, ContractStatus.COMPLETED)
    payment_repo.update_status.assert_called_once_with(payment.id, "released")


# --- No payment exists ---

@pytest.mark.asyncio
async def test_resolve_dispute_no_payment():
    admin = make_admin()
    dispute = make_dispute()
    resolved = make_dispute(status=DisputeStatus.RESOLVED_REFUND)
    resolved.id = dispute.id

    dispute_repo = AsyncMock()
    dispute_repo.get_by_id.return_value = dispute
    dispute_repo.resolve.return_value = resolved
    contract_repo = AsyncMock()
    payment_repo = AsyncMock()
    payment_repo.get_by_contract_id.return_value = None  # no payment

    use_case = make_use_case(dispute_repo, contract_repo, payment_repo)
    result = await use_case.execute(dispute.id, "refund", None, admin)

    assert result.status == DisputeStatus.RESOLVED_REFUND
    payment_repo.update_status.assert_not_called()


# --- Resolution note is optional ---

@pytest.mark.asyncio
async def test_resolve_dispute_without_note():
    admin = make_admin()
    dispute = make_dispute()
    resolved = make_dispute(status=DisputeStatus.RESOLVED_RELEASE)
    resolved.id = dispute.id

    dispute_repo = AsyncMock()
    dispute_repo.get_by_id.return_value = dispute
    dispute_repo.resolve.return_value = resolved
    contract_repo = AsyncMock()
    payment_repo = AsyncMock()
    payment_repo.get_by_contract_id.return_value = None

    use_case = make_use_case(dispute_repo, contract_repo, payment_repo)
    result = await use_case.execute(dispute.id, "release", None, admin)

    dispute_repo.resolve.assert_called_once_with(
        dispute_id=dispute.id,
        status=DisputeStatus.RESOLVED_RELEASE,
        resolved_by=admin.id,
        resolution_note=None,
    )


# --- GetDisputes ---

@pytest.mark.asyncio
async def test_get_disputes_returns_list():
    disputes = [make_dispute(), make_dispute()]
    dispute_repo = AsyncMock()
    dispute_repo.get_all.return_value = disputes

    use_case = GetDisputes(dispute_repo)
    result = await use_case.execute(limit=10, offset=0)

    assert len(result) == 2
    dispute_repo.get_all.assert_called_once_with(limit=10, offset=0)


@pytest.mark.asyncio
async def test_get_disputes_empty():
    dispute_repo = AsyncMock()
    dispute_repo.get_all.return_value = []

    use_case = GetDisputes(dispute_repo)
    result = await use_case.execute()

    assert result == []