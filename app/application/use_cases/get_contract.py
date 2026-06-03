import uuid
from app.application.dto.contract import ContractResponse
from app.infrastructure.repositories.contract_repository import ContractRepository
from app.domain.exceptions import NotFoundError


class GetContract:

    def __init__(self, contract_repo: ContractRepository):
        self.contract_repo = contract_repo

    async def execute(self, contract_id: uuid.UUID) -> ContractResponse:
        contract = await self.contract_repo.get_by_id(contract_id)
        if not contract:
            raise NotFoundError("Contract not found")
        return ContractResponse.model_validate(contract)
