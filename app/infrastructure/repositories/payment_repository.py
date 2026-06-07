import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.payment_repository import IPaymentRepository
from app.domain.entities.payment import PaymentEntity
from app.infrastructure.database.models.payment import Payment, PaymentStatus

PLATFORM_FEE_PERCENT = 10.0  # 10% комиссия платформы


def _to_entity(p: Payment) -> PaymentEntity:
    return PaymentEntity(
        id=p.id,
        contract_id=p.contract_id,
        client_id=p.client_id,
        freelancer_id=p.freelancer_id,
        amount=float(p.amount),
        platform_fee=float(p.platform_fee),
        freelancer_amount=float(p.freelancer_amount),
        status=p.status,
        created_at=p.created_at,
        updated_at=p.updated_at,
        stripe_payment_intent_id=p.stripe_payment_intent_id,
        stripe_transfer_id=p.stripe_transfer_id,
    )


class PaymentRepository(IPaymentRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        contract_id: uuid.UUID,
        client_id: uuid.UUID,
        freelancer_id: uuid.UUID,
        amount: float,
        platform_fee_percent: float = PLATFORM_FEE_PERCENT,
    ) -> PaymentEntity:
        platform_fee = round(amount * platform_fee_percent / 100, 2)
        freelancer_amount = round(amount - platform_fee, 2)

        payment = Payment(
            contract_id=contract_id,
            client_id=client_id,
            freelancer_id=freelancer_id,
            amount=amount,
            platform_fee=platform_fee,
            freelancer_amount=freelancer_amount,
            status=PaymentStatus.PENDING,
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return _to_entity(payment)

    async def get_by_contract_id(self, contract_id: uuid.UUID) -> PaymentEntity | None:
        stmt = select(Payment).where(Payment.contract_id == contract_id)
        result = await self.db.execute(stmt)
        p = result.scalar_one_or_none()
        return _to_entity(p) if p else None

    async def update_status(
        self,
        payment_id: uuid.UUID,
        status: str,
        stripe_payment_intent_id: str | None = None,
        stripe_transfer_id: str | None = None,
    ) -> PaymentEntity:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await self.db.execute(stmt)
        payment = result.scalar_one()
        payment.status = PaymentStatus(status)
        if stripe_payment_intent_id:
            payment.stripe_payment_intent_id = stripe_payment_intent_id
        if stripe_transfer_id:
            payment.stripe_transfer_id = stripe_transfer_id
        await self.db.commit()
        await self.db.refresh(payment)
        return _to_entity(payment)
