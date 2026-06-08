import uuid
import pytest
from unittest.mock import AsyncMock
from datetime import datetime
from decimal import Decimal
from app.application.use_cases.update_contract_status import UpdateContractStatus
from app.domain.entities.contract import ContractEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.database.models.contract import ContractStatus


def make_client():
    return UserEntity(
        id=uuid.uuid4(), email="c@test.com", full_name="Client",
        role=UserRole.CLIENT, is_active=True, created_at=datetime.now(),
    )

def make_contract(client_id, freelancer_id, status=ContractStatus.ACTIVE):
    return ContractEntity(
        id=uuid.uuid4(), job_id=uuid.uuid4(), proposal_id=uuid.uuid4(),
        client_id=client_id, freelancer_id=freelancer_id,
        agreed_rate=Decimal("500"), status=status, created_at=datetime.now(),
    )


@pytest.mark.asyncio
async def test_complete_contract_success():
    client = make_client()
    freelancer_id = uuid.uuid4()
    contract = make_contract(client.id, freelancer_id)

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = contract
    mock_repo.update_status.return_value = ContractEntity(
        **{**contract.__dict__, "status": ContractStatus.COMPLETED}
    )

    use_case = UpdateContractStatus(mock_repo)
    result = await use_case.execute(contract.id, ContractStatus.COMPLETED, client)

    assert result.status == ContractStatus.COMPLETED
    mock_repo.update_status.assert_called_once()


@pytest.mark.asyncio
async def test_complete_contract_not_found():
    client = make_client()
    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = None

    use_case = UpdateContractStatus(mock_repo)

    with pytest.raises(NotFoundError):
        await use_case.execute(uuid.uuid4(), ContractStatus.COMPLETED, client)


@pytest.mark.asyncio
async def test_complete_contract_wrong_user():
    client = make_client()
    other_client = make_client()
    contract = make_contract(other_client.id, uuid.uuid4())

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = contract

    use_case = UpdateContractStatus(mock_repo)

    with pytest.raises(ForbiddenError):
        await use_case.execute(contract.id, ContractStatus.COMPLETED, client)


@pytest.mark.asyncio
async def test_complete_already_completed_contract():
    client = make_client()
    contract = make_contract(client.id, uuid.uuid4(), status=ContractStatus.COMPLETED)

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = contract

    use_case = UpdateContractStatus(mock_repo)

    with pytest.raises(ValidationError):
        await use_case.execute(contract.id, ContractStatus.COMPLETED, client)


@pytest.mark.asyncio
async def test_complete_contract_freelancer_forbidden():
    client_id = uuid.uuid4()
    freelancer = UserEntity(
        id=uuid.uuid4(), email="f@test.com", full_name="Freelancer",
        role=UserRole.FREELANCER, is_active=True, created_at=datetime.now(),
    )
    contract = make_contract(client_id, freelancer.id)

    mock_repo = AsyncMock()
    mock_repo.get_by_id.return_value = contract

    use_case = UpdateContractStatus(mock_repo)

    with pytest.raises(ForbiddenError):
        await use_case.execute(contract.id, ContractStatus.COMPLETED, freelancer)