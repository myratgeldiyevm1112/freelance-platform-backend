import uuid
from app.domain.entities.user import UserEntity
from app.domain.exceptions import NotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.database.models.user import User


class GetAllUsers:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, limit: int = 20, offset: int = 0) -> list[UserEntity]:
        from app.infrastructure.repositories.user_repository import UserRepository
        stmt = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        repo = UserRepository(self.db)
        return [repo._to_entity(u) for u in result.scalars().all()]


class BanUser:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, user_id: uuid.UUID) -> UserEntity:
        from app.infrastructure.repositories.user_repository import UserRepository
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        return UserRepository(self.db)._to_entity(user)


class UnbanUser:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, user_id: uuid.UUID) -> UserEntity:
        from app.infrastructure.repositories.user_repository import UserRepository
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        user.is_active = True
        await self.db.commit()
        await self.db.refresh(user)
        return UserRepository(self.db)._to_entity(user)
