import uuid
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.job_repository import IJobRepository
from app.domain.entities.job import JobEntity
from app.infrastructure.database.models.job import Job, JobStatus


class JobRepository(IJobRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: Job) -> JobEntity:
        return JobEntity(
            id=model.id,
            client_id=model.client_id,
            title=model.title,
            description=model.description,
            budget=model.budget,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(self, entity: JobEntity) -> JobEntity:
        job = Job(
            id=entity.id,
            client_id=entity.client_id,
            title=entity.title,
            description=entity.description,
            budget=entity.budget,
            status=JobStatus.OPEN,
        )
        self.session.add(job)
        await self.session.flush()
        return self._to_entity(job)

    async def get_by_id(self, job_id: uuid.UUID) -> JobEntity | None:
        result = await self.session.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        return self._to_entity(job) if job else None


    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
        min_budget: float | None = None,
        max_budget: float | None = None,
    ) -> list[JobEntity]:
        query = select(Job)
        filters = []

        if status:
            filters.append(Job.status == status)
        if min_budget is not None:
            filters.append(Job.budget >= min_budget)
        if max_budget is not None:
            filters.append(Job.budget <= max_budget)
        if filters:
            query = query.where(and_(*filters))

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return [self._to_entity(j) for j in result.scalars().all()]
    async def count(
        self,
        status: str | None = None,
        min_budget: float | None = None,
        max_budget: float | None = None,
    ) -> int:
        from sqlalchemy import func
        query = select(func.count(Job.id))
        filters = []
        if status:
            filters.append(Job.status == status)
        if min_budget is not None:
            filters.append(Job.budget >= min_budget)
        if max_budget is not None:
            filters.append(Job.budget <= max_budget)
        if filters:
            query = query.where(and_(*filters))
        result = await self.session.execute(query)
        return result.scalar_one()