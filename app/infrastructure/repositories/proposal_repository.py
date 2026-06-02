import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.proposal_repository import IProposalRepository
from app.domain.entities.proposal import ProposalEntity
from app.infrastructure.database.models.proposal import Proposal, ProposalStatus


class ProposalRepository(IProposalRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Proposal) -> ProposalEntity:
        return ProposalEntity(
            id=model.id,
            job_id=model.job_id,
            freelancer_id=model.freelancer_id,
            cover_letter=model.cover_letter,
            proposed_rate=model.proposed_rate,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, entity: ProposalEntity) -> ProposalEntity:
        proposal = Proposal(
            id=entity.id,
            job_id=entity.job_id,
            freelancer_id=entity.freelancer_id,
            cover_letter=entity.cover_letter,
            proposed_rate=entity.proposed_rate,
            status=ProposalStatus.PENDING,
        )
        self.session.add(proposal)
        await self.session.flush()
        return self._to_entity(proposal)

    async def get_by_id(self, proposal_id: uuid.UUID) -> ProposalEntity | None:
        result = await self.session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        proposal = result.scalar_one_or_none()
        return self._to_entity(proposal) if proposal else None

    async def get_by_job_id(self, job_id: uuid.UUID) -> list[ProposalEntity]:
        result = await self.session.execute(
            select(Proposal).where(Proposal.job_id == job_id)
        )
        return [self._to_entity(p) for p in result.scalars().all()]

    async def get_by_freelancer_and_job(
        self, freelancer_id: uuid.UUID, job_id: uuid.UUID
    ) -> ProposalEntity | None:
        result = await self.session.execute(
            select(Proposal).where(
                Proposal.freelancer_id == freelancer_id,
                Proposal.job_id == job_id,
            )
        )
        proposal = result.scalar_one_or_none()
        return self._to_entity(proposal) if proposal else None

    async def update_status(
        self, proposal_id: uuid.UUID, status: str
    ) -> ProposalEntity:
        result = await self.session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        proposal = result.scalar_one_or_none()
        if not proposal:
            raise ValueError("Proposal not found")
        proposal.status = status
        await self.session.flush()
        return self._to_entity(proposal)
