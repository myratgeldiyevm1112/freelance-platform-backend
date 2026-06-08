import uuid
from app.application.interfaces.dispute_repository import IDisputeRepository
from app.application.interfaces.contract_repository import IContractRepository
from app.domain.entities.dispute import DisputeEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundError, ForbiddenError, ConflictError
from app.infrastructure.database.models.dispute import DisputeStatus
from app.infrastructure.database.models.contract import ContractStatus


class OpenDispute:
    def __init__(self, dispute_repo: IDisputeRepository, contract_repo: IContractRepository):
        self.dispute_repo = dispute_repo
        self.contract_repo = contract_repo

    async def execute(
        self,
        contract_id: uuid.UUID,
        reason: str,
        current_user: UserEntity,
    ) -> DisputeEntity:
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise NotFoundError("Contract not found")

        if current_user.id not in (contract.client_id, contract.freelancer_id):
            raise ForbiddenError("You are not a participant of this contract")

        if contract.status != ContractStatus.ACTIVE:
            raise ForbiddenError("Can only dispute active contracts")

        existing = await self.dispute_repo.get_by_contract_id(contract_id)
        open_disputes = [d for d in existing if d.status == DisputeStatus.OPEN]
        if open_disputes:
            raise ConflictError("There is already an open dispute for this contract")

        return await self.dispute_repo.create(
            contract_id=contract_id,
            opened_by=current_user.id,
            reason=reason,
        )
