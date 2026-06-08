import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.dispute import OpenDisputeRequest, ResolveDisputeRequest, DisputeResponse
from app.application.use_cases.open_dispute import OpenDispute
from app.application.use_cases.resolve_dispute import ResolveDispute, GetDisputes
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.dispute_repository import DisputeRepository
from app.infrastructure.repositories.contract_repository import ContractRepository
from app.infrastructure.repositories.payment_repository import PaymentRepository

router = APIRouter(prefix="/disputes", tags=["Disputes"])


@router.post("/", response_model=DisputeResponse, status_code=201)
async def open_dispute(
    data: OpenDisputeRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = OpenDispute(DisputeRepository(db), ContractRepository(db))
    return await use_case.execute(
        contract_id=data.contract_id,
        reason=data.reason,
        current_user=current_user,
    )


@router.get("/admin", response_model=list[DisputeResponse])
async def get_all_disputes(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetDisputes(DisputeRepository(db))
    return await use_case.execute(limit=limit, offset=offset)


@router.patch("/{dispute_id}/resolve", response_model=DisputeResponse)
async def resolve_dispute(
    dispute_id: uuid.UUID,
    data: ResolveDisputeRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = ResolveDispute(DisputeRepository(db), ContractRepository(db), PaymentRepository(db))
    return await use_case.execute(
        dispute_id=dispute_id,
        resolution=data.resolution,
        resolution_note=data.resolution_note,
        current_user=current_user,
    )
