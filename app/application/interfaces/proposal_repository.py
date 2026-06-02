from abc import ABC, abstractmethod
import uuid
from app.domain.entities.proposal import ProposalEntity


class IProposalRepository(ABC):

    @abstractmethod
    async def create(self, entity: ProposalEntity) -> ProposalEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, proposal_id: uuid.UUID) -> ProposalEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_job_id(self, job_id: uuid.UUID) -> list[ProposalEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_freelancer_and_job(
        self, freelancer_id: uuid.UUID, job_id: uuid.UUID
    ) -> ProposalEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def update_status(
        self, proposal_id: uuid.UUID, status: str
    ) -> ProposalEntity:
        raise NotImplementedError
