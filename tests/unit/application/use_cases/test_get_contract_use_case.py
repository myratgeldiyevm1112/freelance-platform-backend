import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.application.use_cases.get_contract import GetContract
from app.domain.entities.contract import ContractEntity
from app.domain.exceptions import NotFoundError
from app.infrastructure.database.models.contract import ContractStatus


@pytest.mark.asyncio
async def test_get_contract_success():
    contract_id = uuid.uuid4()

    contract = ContractEntity(
        id=contract_id,
        job_id=uuid.uuid4(),
        proposal_id=uuid.uuid4(),
        client_id=uuid.uuid4(),
        freelancer_id=uuid.uuid4(),
        agreed_rate=100.0,
        status=ContractStatus.ACTIVE,
        created_at=datetime.now(timezone.utc)
    )

    repo = AsyncMock()
    repo.get_by_id.return_value = contract

    use_case = GetContract(repo)

    result = await use_case.execute(contract_id, current_user_id=contract.client_id)

    assert result.id == contract.id
    repo.get_by_id.assert_awaited_once_with(contract_id)


@pytest.mark.asyncio
async def test_get_contract_not_found():
    contract_id = uuid.uuid4()

    repo = AsyncMock()
    repo.get_by_id.return_value = None

    use_case = GetContract(repo)

    with pytest.raises(NotFoundError, match="Contract not found"):
        await use_case.execute(contract_id, current_user_id=uuid.uuid4())

    repo.get_by_id.assert_awaited_once_with(contract_id)

from app.domain.exceptions import ForbiddenError

@pytest.mark.asyncio
async def test_get_contract_forbidden_for_stranger():
    contract_id = uuid.uuid4()

    contract = ContractEntity(
        id=contract_id,
        job_id=uuid.uuid4(),
        proposal_id=uuid.uuid4(),
        client_id=uuid.uuid4(),     # Владелец один UUID
        freelancer_id=uuid.uuid4(), # Исполнитель другой UUID
        agreed_rate=100.0,
        status=ContractStatus.ACTIVE,
        created_at=datetime.now(timezone.utc)
    )

    repo = AsyncMock()
    repo.get_by_id.return_value = contract
    use_case = GetContract(repo)

    # Передаем абсолютно левый UUID, которого нет в контракте
    with pytest.raises(ForbiddenError, match="You do not have access to this contract"):
        await use_case.execute(contract_id, current_user_id=uuid.uuid4())