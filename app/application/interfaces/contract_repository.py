from abc import ABC, abstractmethod
import uuid
from app.domain.entities.contract import ContractEntity
from app.infrastructure.database.models.contract import ContractStatus

class IContractRepository(ABC):

    @abstractmethod
    async def get_by_id(self, contract_id: uuid.UUID) -> ContractEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def update_status(self, contract_id: uuid.UUID, new_status: ContractStatus) -> ContractEntity | None:
        raise NotImplementedError
