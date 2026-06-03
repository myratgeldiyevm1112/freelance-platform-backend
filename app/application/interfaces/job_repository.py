from abc import ABC, abstractmethod
from app.domain.entities.job import JobEntity


class IJobRepository(ABC):

    @abstractmethod
    async def create(self, entity: JobEntity) -> JobEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, job_id) -> JobEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self,
        skip: int,
        limit: int,
        status: str | None = None,
        min_budget: float | None = None,
        max_budget: float | None = None,
    ) -> list[JobEntity]:
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        status: str | None = None,
        min_budget: float | None = None,
        max_budget: float | None = None,
    ) -> int:
        raise NotImplementedError
