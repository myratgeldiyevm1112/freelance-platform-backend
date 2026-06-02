from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.contract import UpdateContractStatusRequest, ContractResponse
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
    repo = ContractRepository(db)
    contract = await repo.get_by_id(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    return ContractResponse.model_validate(contract)


@router.patch("/{contract_id}/status", response_model=ContractResponse)
async def update_contract_status(
    contract_id: UUID,
    data: UpdateContractStatusRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ContractRepository(db)
    use_case = UpdateContractStatus(repo)
    try:
        return await use_case.execute(
            contract_id=contract_id,
            new_status=data.new_status,
            current_user=current_user,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))