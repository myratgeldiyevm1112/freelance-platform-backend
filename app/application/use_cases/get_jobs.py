import uuid
from app.application.dto.job import JobResponse
from app.application.interfaces.job_repository import IJobRepository
from app.domain.exceptions import NotFoundError
from app.application.dto.pagination import PaginationParams, PaginatedResponse
from app.infrastructure.cache.jobs_cache import JobsCache


class GetJobs:

    def __init__(self, job_repo: IJobRepository, cache: JobsCache | None = None):
        self.job_repo = job_repo
        self.cache = cache

    async def execute(
        self,
        params: PaginationParams,
        status: str | None = None,
        min_budget: float | None = None,
        max_budget: float | None = None,
    ) -> PaginatedResponse[JobResponse]:

        if self.cache:
            cached = await self.cache.get(
                params.page, params.page_size, status, min_budget, max_budget
            )
            if cached:
                return PaginatedResponse[JobResponse](**cached)

        jobs = await self.job_repo.get_all(
            skip=params.skip,
            limit=params.limit,
            status=status,
            min_budget=min_budget,
            max_budget=max_budget,
        )
        total = await self.job_repo.count(
            status=status,
            min_budget=min_budget,
            max_budget=max_budget,
        )
        items = [JobResponse.model_validate(j) for j in jobs]
        result = PaginatedResponse.create(items=items, total=total, params=params)

        if self.cache:
            await self.cache.set(
                params.page, params.page_size, status, min_budget, max_budget,
                result.model_dump()
            )

        return result

    async def execute_one(self, job_id: uuid.UUID) -> JobResponse:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        return JobResponse.model_validate(job)