from abc import ABC, abstractmethod
import uuid
from app.domain.entities.review import ReviewEntity

class IReviewRepository(ABC):

    @abstractmethod
    async def create(self, entity: ReviewEntity) -> ReviewEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_by_contract_id(self, contract_id: uuid.UUID) -> ReviewEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_reviewee_id(self, reviewee_id: uuid.UUID) -> list[ReviewEntity]:
        raise NotImplementedError
