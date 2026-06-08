from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.infrastructure.database.models.user import User
from app.infrastructure.database.models.job import Job
from app.infrastructure.database.models.contract import Contract, ContractStatus
from app.infrastructure.database.models.payment import Payment, PaymentStatus
from app.infrastructure.database.models.dispute import Dispute, DisputeStatus


class GetPlatformStats:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self) -> dict:
        total_users = await self.db.scalar(select(func.count()).select_from(User))
        total_jobs = await self.db.scalar(select(func.count()).select_from(Job))
        total_contracts = await self.db.scalar(select(func.count()).select_from(Contract))
        active_contracts = await self.db.scalar(
            select(func.count()).where(Contract.status == ContractStatus.ACTIVE)
        )
        completed_contracts = await self.db.scalar(
            select(func.count()).where(Contract.status == ContractStatus.COMPLETED)
        )
        total_revenue = await self.db.scalar(
            select(func.sum(Payment.platform_fee)).where(
                Payment.status == PaymentStatus.RELEASED
            )
        )
        open_disputes = await self.db.scalar(
            select(func.count()).where(Dispute.status == DisputeStatus.OPEN)
        )

        return {
            "total_users": total_users or 0,
            "total_jobs": total_jobs or 0,
            "total_contracts": total_contracts or 0,
            "active_contracts": active_contracts or 0,
            "completed_contracts": completed_contracts or 0,
            "total_platform_revenue": float(total_revenue or 0),
            "open_disputes": open_disputes or 0,
        }
