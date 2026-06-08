import uuid
from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app.application.use_cases.open_dispute import OpenDispute
from app.domain.entities.contract import ContractEntity
from app.domain.entities.dispute import DisputeEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import (
    NotFoundError,
    ForbiddenError,
    ConflictError,
)
from app.infrastructure.database.models.contract import ContractStatus
from app.infrastructure.database.models.dispute import DisputeStatus
from app.infrastructure.database.models.user import UserRole


def make_user(user_id):
    return UserEntity(
        id=user_id,
        email="test@test.com",
        full_name="Test User",
        role=UserRole.CLIENT,
        is_active=True,
        created_at=datetime.utcnow(),
    )


def make_contract(client_id, freelancer_id, status=ContractStatus.ACTIVE):
    return ContractEntity(
        id=uuid.uuid4(),
        job_id=uuid.uuid4(),
        proposal_id=uuid.uuid4(),
        client_id=client_id,
        freelancer_id=freelancer_id,
        agreed_rate=100.0,
        status=status,
        created_at=datetime.utcnow(),
    )


@pytest.mark.asyncio
async def test_open_dispute_contract_not_found():
    dispute_repo = AsyncMock()
    contract_repo = AsyncMock()

    contract_repo.get_by_id.return_value = None

    use_case = OpenDispute(dispute_repo, contract_repo)

    with pytest.raises(NotFoundError):
        await use_case.execute(
            uuid.uuid4(),
            "Problem",
            make_user(uuid.uuid4()),
        )


@pytest.mark.asyncio
async def test_open_dispute_user_not_participant():
    dispute_repo = AsyncMock()
    contract_repo = AsyncMock()

    contract = make_contract(uuid.uuid4(), uuid.uuid4())

    contract_repo.get_by_id.return_value = contract

    use_case = OpenDispute(dispute_repo, contract_repo)

    with pytest.raises(ForbiddenError):
        await use_case.execute(
            contract.id,
            "Problem",
            make_user(uuid.uuid4()),
        )


@pytest.mark.asyncio
async def test_open_dispute_contract_not_active():
    dispute_repo = AsyncMock()
    contract_repo = AsyncMock()

    client_id = uuid.uuid4()

    contract = make_contract(
        client_id,
        uuid.uuid4(),
        ContractStatus.COMPLETED,
    )

    contract_repo.get_by_id.return_value = contract

    use_case = OpenDispute(dispute_repo, contract_repo)

    with pytest.raises(ForbiddenError):
        await use_case.execute(
            contract.id,
            "Problem",
            make_user(client_id),
        )


@pytest.mark.asyncio
async def test_open_dispute_already_exists():
    dispute_repo = AsyncMock()
    contract_repo = AsyncMock()

    client_id = uuid.uuid4()

    contract = make_contract(client_id, uuid.uuid4())

    existing_dispute = DisputeEntity(
        id=uuid.uuid4(),
        contract_id=contract.id,
        opened_by=client_id,
        reason="Old dispute",
        status=DisputeStatus.OPEN,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    contract_repo.get_by_id.return_value = contract
    dispute_repo.get_by_contract_id.return_value = [existing_dispute]

    use_case = OpenDispute(dispute_repo, contract_repo)

    with pytest.raises(ConflictError):
        await use_case.execute(
            contract.id,
            "Problem",
            make_user(client_id),
        )


@pytest.mark.asyncio
async def test_open_dispute_success():
    dispute_repo = AsyncMock()
    contract_repo = AsyncMock()

    client_id = uuid.uuid4()

    contract = make_contract(client_id, uuid.uuid4())

    created_dispute = DisputeEntity(
        id=uuid.uuid4(),
        contract_id=contract.id,
        opened_by=client_id,
        reason="Problem",
        status=DisputeStatus.OPEN,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    contract_repo.get_by_id.return_value = contract
    dispute_repo.get_by_contract_id.return_value = []
    dispute_repo.create.return_value = created_dispute

    use_case = OpenDispute(dispute_repo, contract_repo)

    result = await use_case.execute(
        contract.id,
        "Problem",
        make_user(client_id),
    )

    assert result == created_dispute

    dispute_repo.create.assert_awaited_once()
