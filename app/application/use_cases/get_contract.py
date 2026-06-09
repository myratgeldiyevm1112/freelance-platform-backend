import uuid
from app.application.dto.contract import ContractResponse
from app.infrastructure.repositories.contract_repository import ContractRepository
from app.domain.exceptions import NotFoundError, ForbiddenError


class GetContract:

    def __init__(self, contract_repo: ContractRepository):
        self.contract_repo = contract_repo

    async def execute(self, contract_id: uuid.UUID, current_user_id: uuid.UUID, is_admin: bool = False) -> ContractResponse:
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise NotFoundError("Contract not found")
        if not is_admin and contract.client_id != current_user_id and contract.freelancer_id != current_user_id:
            raise ForbiddenError("You do not have access to this contract")
        return ContractResponse.model_validate(contract)
