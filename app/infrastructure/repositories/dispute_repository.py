import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.dispute_repository import IDisputeRepository
from app.domain.entities.dispute import DisputeEntity
from app.infrastructure.database.models.dispute import Dispute, DisputeStatus
from app.domain.exceptions import NotFoundError


def _to_entity(d: Dispute) -> DisputeEntity:
    return DisputeEntity(
        id=d.id,
        contract_id=d.contract_id,
        opened_by=d.opened_by,
        reason=d.reason,
        status=d.status,
        created_at=d.created_at,
        updated_at=d.updated_at,
        resolution_note=d.resolution_note,
        resolved_by=d.resolved_by,
    )


class DisputeRepository(IDisputeRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        contract_id: uuid.UUID,
        opened_by: uuid.UUID,
        reason: str,
    ) -> DisputeEntity:
        dispute = Dispute(
            contract_id=contract_id,
            opened_by=opened_by,
            reason=reason,
            status=DisputeStatus.OPEN,
        )
        self.db.add(dispute)
        await self.db.commit()
        await self.db.refresh(dispute)
        return _to_entity(dispute)

    async def get_by_id(self, dispute_id: uuid.UUID) -> DisputeEntity | None:
        result = await self.db.execute(select(Dispute).where(Dispute.id == dispute_id))
        d = result.scalar_one_or_none()
        return _to_entity(d) if d else None

    async def get_all(self, limit: int = 20, offset: int = 0) -> list[DisputeEntity]:
        stmt = select(Dispute).order_by(Dispute.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return [_to_entity(d) for d in result.scalars().all()]

    async def get_by_contract_id(self, contract_id: uuid.UUID) -> list[DisputeEntity]:
        stmt = select(Dispute).where(Dispute.contract_id == contract_id)
        result = await self.db.execute(stmt)
        return [_to_entity(d) for d in result.scalars().all()]

    async def resolve(
        self,
        dispute_id: uuid.UUID,
        status: DisputeStatus,
        resolved_by: uuid.UUID,
        resolution_note: str | None = None,
    ) -> DisputeEntity:
        result = await self.db.execute(select(Dispute).where(Dispute.id == dispute_id))
        dispute = result.scalar_one_or_none()
        if not dispute:
            raise NotFoundError("Dispute not found")
        dispute.status = status
        dispute.resolved_by = resolved_by
        dispute.resolution_note = resolution_note
        await self.db.commit()
        await self.db.refresh(dispute)
        return _to_entity(dispute)
