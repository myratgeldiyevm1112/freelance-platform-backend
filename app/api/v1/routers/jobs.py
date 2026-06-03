import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.job import CreateJobRequest, JobResponse
from app.application.use_cases.create_job import CreateJob
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.job_repository import JobRepository
from app.application.use_cases.get_jobs import GetJobs
from app.infrastructure.database.models.job import JobStatus

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: CreateJobRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = CreateJob(JobRepository(db))
    return await use_case.execute(data, current_user)


@router.get("/", response_model=list[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 20,
    status: JobStatus | None = None,
    min_budget: float | None = None,
    max_budget: float | None = None,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetJobs(JobRepository(db))
    return await use_case.execute(
        skip=skip,
        limit=limit,
        status=status,
        min_budget=min_budget,
        max_budget=max_budget,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetJobs(JobRepository(db))
    return await use_case.execute_one(job_id)
