import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.entities.contract import ContractEntity
from app.infrastructure.database.models.contract import Contract, ContractStatus


class ContractRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Contract) -> ContractEntity:
        return ContractEntity(
            id=model.id,
            job_id=model.job_id,
            proposal_id=model.proposal_id,
            client_id=model.client_id,
            freelancer_id=model.freelancer_id,
            agreed_rate=model.agreed_rate,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, entity: ContractEntity) -> ContractEntity:
        contract = Contract(
            id=entity.id,
            job_id=entity.job_id,
            proposal_id=entity.proposal_id,
            client_id=entity.client_id,
            freelancer_id=entity.freelancer_id,
            agreed_rate=entity.agreed_rate,
            status=ContractStatus.ACTIVE,
        )
        self.session.add(contract)
        await self.session.flush()
        await self.session.refresh(contract)
        return self._to_entity(contract)

    async def get_by_id(self, contract_id: uuid.UUID) -> ContractEntity | None:
        result = await self.session.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        contract = result.scalar_one_or_none()
        return self._to_entity(contract) if contract else None

    async def update_status(self, contract_id: uuid.UUID, new_status: ContractStatus) -> ContractEntity | None:
        result = await self.session.execute(
            select(Contract).where(Contract.id == contract_id)
        )
        contract = result.scalar_one_or_none()
        if not contract:
            return None
        contract.status = new_status
        await self.session.flush()
        await self.session.refresh(contract)
        return self._to_entity(contract)