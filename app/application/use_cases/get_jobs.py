import uuid
from app.application.dto.job import JobResponse
from app.application.interfaces.job_repository import IJobRepository
from app.domain.exceptions import NotFoundError
from app.application.dto.pagination import PaginationParams, PaginatedResponse


class GetJobs:

    def __init__(self, job_repo: IJobRepository):
        self.job_repo = job_repo

    async def execute(
        self,
        params: PaginationParams,
        status: str | None = None,
        min_budget: float | None = None,
        max_budget: float | None = None,
    ) -> PaginatedResponse[JobResponse]:
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
        return PaginatedResponse.create(items=items, total=total, params=params)

        
    async def execute_one(self, job_id: uuid.UUID) -> JobResponse:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        return JobResponse.model_validate(job)