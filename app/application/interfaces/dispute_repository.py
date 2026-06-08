import uuid
from abc import ABC, abstractmethod
from app.domain.entities.dispute import DisputeEntity
from app.infrastructure.database.models.dispute import DisputeStatus


class IDisputeRepository(ABC):

    @abstractmethod
    async def create(
        self,
        contract_id: uuid.UUID,
        opened_by: uuid.UUID,
        reason: str,
    ) -> DisputeEntity:
        pass

    @abstractmethod
    async def get_by_id(self, dispute_id: uuid.UUID) -> DisputeEntity | None:
        pass

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> list[DisputeEntity]:
        pass

    @abstractmethod
    async def get_by_contract_id(self, contract_id: uuid.UUID) -> list[DisputeEntity]:
        pass

    @abstractmethod
    async def resolve(
        self,
        dispute_id: uuid.UUID,
        status: DisputeStatus,
        resolved_by: uuid.UUID,
        resolution_note: str | None,
    ) -> DisputeEntity:
        pass
