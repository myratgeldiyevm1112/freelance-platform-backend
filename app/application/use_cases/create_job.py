import uuid
from app.application.dto.job import CreateJobRequest, JobResponse
from app.application.interfaces.job_repository import IJobRepository
from app.domain.entities.job import JobEntity
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.user import UserRole
from app.domain.exceptions import ForbiddenError
from app.infrastructure.cache.jobs_cache import JobsCache


class CreateJob:

    def __init__(self, job_repo: IJobRepository, cache: JobsCache | None = None):
        self.job_repo = job_repo
        self.cache = cache

    async def execute(self, data: CreateJobRequest, current_user: UserEntity) -> JobResponse:
        if current_user.role != UserRole.CLIENT:
            raise ForbiddenError("Only clients can create jobs")

        entity = JobEntity(
            id=uuid.uuid4(),
            client_id=current_user.id,
            title=data.title,
            description=data.description,
            budget=data.budget,
            status=None,
            created_at=None,
            required_skills=data.required_skills,
        )
        created = await self.job_repo.create(entity)

        if self.cache:
            await self.cache.invalidate_all()

        return JobResponse.model_validate(created)