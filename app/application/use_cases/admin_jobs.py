import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.domain.entities.job import JobEntity
from app.domain.exceptions import NotFoundError
from app.infrastructure.database.models.job import Job


class GetAllJobs:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, limit: int = 20, offset: int = 0) -> list:
        from app.infrastructure.repositories.job_repository import JobRepository
        stmt = select(Job).order_by(Job.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        repo = JobRepository(self.db)
        return [repo._to_entity(j) for j in result.scalars().all()]


class DeleteJob:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, job_id: uuid.UUID) -> None:
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise NotFoundError("Job not found")
        await self.db.delete(job)
        await self.db.commit()
