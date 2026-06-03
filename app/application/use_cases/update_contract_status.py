import uuid
from app.application.dto.contract import ContractResponse
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.contract import ContractStatus
from app.infrastructure.database.models.user import UserRole
from app.infrastructure.repositories.contract_repository import ContractRepository
from app.domain.exceptions import NotFoundError, ForbiddenError, ValidationError


class UpdateContractStatus:

    def __init__(self, contract_repo: ContractRepository):
        self.contract_repo = contract_repo

    async def execute(
        self,
        contract_id: uuid.UUID,
        new_status: ContractStatus,
        current_user: UserEntity,
    ) -> ContractResponse:
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise NotFoundError("Contract not found")

        if current_user.id not in (contract.client_id, contract.freelancer_id):
            raise ForbiddenError("You are not a participant of this contract")

        if contract.status != ContractStatus.ACTIVE:
            raise ValidationError("Only active contracts can be updated")

        if new_status == ContractStatus.COMPLETED and current_user.role != UserRole.CLIENT:
            raise ForbiddenError("Only the client can mark a contract as completed")

        updated = await self.contract_repo.update_status(contract_id, new_status)
        return ContractResponse.model_validate(updated)
