from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.contract import UpdateContractStatusRequest, ContractResponse
from app.application.use_cases.get_contract import GetContract
from app.application.use_cases.update_contract_status import UpdateContractStatus
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.contract_repository import ContractRepository

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: UUID,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetContract(ContractRepository(db))
    return await use_case.execute(contract_id)


@router.patch("/{contract_id}/status", response_model=ContractResponse)
async def update_contract_status(
    contract_id: UUID,
    data: UpdateContractStatusRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = UpdateContractStatus(ContractRepository(db))
    return await use_case.execute(
        contract_id=contract_id,
        new_status=data.new_status,
        current_user=current_user,
    )