import uuid
from app.application.dto.job import JobResponse
from app.application.interfaces.job_repository import IJobRepository
from app.domain.exceptions import NotFoundError


class GetJobs:

    def __init__(self, job_repo: IJobRepository):
        self.job_repo = job_repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        min_budget: float | None = None,
        max_budget: float | None = None,
    ) -> list[JobResponse]:
        jobs = await self.job_repo.get_all(
            skip=skip,
            limit=limit,
            status=status,
            min_budget=min_budget,
            max_budget=max_budget,
        )
        return [JobResponse.model_validate(j) for j in jobs]
    
    async def execute_one(self, job_id: uuid.UUID) -> JobResponse | None:
        job = await self.job_repo.get_by_id(job_id)
        if not job:
            raise NotFoundError("Job not found")
        return JobResponse.model_validate(job)