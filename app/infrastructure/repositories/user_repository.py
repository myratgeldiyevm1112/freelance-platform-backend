import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.user_repository import IUserRepository
from app.domain.entities.user import UserEntity
from app.infrastructure.database.models.user import User


class UserRepository(IUserRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: User) -> UserEntity:
        return UserEntity(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
            bio=model.bio,
            hourly_rate=model.hourly_rate,
        )

    async def create(self, entity: UserEntity, hashed_password: str) -> UserEntity:
        user = User(
            id=entity.id,
            email=entity.email,
            full_name=entity.full_name,
            role=entity.role,
            hashed_password=hashed_password,
            is_active=entity.is_active,
        )
        self.session.add(user)
        await self.session.flush()
        return self._to_entity(user)

    async def get_by_email(self, email: str) -> UserEntity | None:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return self._to_entity(user) if user else None

    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return self._to_entity(user) if user else None
