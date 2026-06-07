import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.payment import CreatePaymentRequest, PaymentIntentResponse, PaymentResponse
from app.application.use_cases.create_payment import CreatePayment
from app.application.use_cases.release_payment import ReleasePayment
from app.application.use_cases.refund_payment import RefundPayment
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.payment_repository import PaymentRepository
from app.infrastructure.repositories.contract_repository import ContractRepository

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/contracts/{contract_id}", response_model=PaymentIntentResponse, status_code=201)
async def create_payment(
    contract_id: uuid.UUID,
    data: CreatePaymentRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = CreatePayment(PaymentRepository(db), ContractRepository(db))
    return await use_case.execute(contract_id, current_user, data.freelancer_id)


@router.post("/contracts/{contract_id}/release", response_model=PaymentResponse)
async def release_payment(
    contract_id: uuid.UUID,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = ReleasePayment(PaymentRepository(db))
    return await use_case.execute(contract_id, current_user)


@router.post("/contracts/{contract_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    contract_id: uuid.UUID,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = RefundPayment(PaymentRepository(db))
    return await use_case.execute(contract_id, current_user)
