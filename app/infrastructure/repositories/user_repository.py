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
            avatar_url=model.avatar_url,
            portfolio_urls=model.portfolio_urls,
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

    async def get_hashed_password(self, email: str) -> str | None:
        result = await self.session.execute(
            select(User.hashed_password).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def update(self, user_id, data) -> UserEntity:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        await self.session.flush()
        return self._to_entity(user)

    async def update_avatar(self, user_id: uuid.UUID, url: str) -> None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.avatar_url = url
            await self.session.flush()

    async def update_portfolio(self, user_id: uuid.UUID, urls: list) -> None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.portfolio_urls = urls
            await self.session.flush()
    async def search_freelancers(
        self,
        skill: str | None = None,
        min_rate: float | None = None,
        max_rate: float | None = None,
        min_rating: float | None = None,
        q: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[UserEntity]:
        from sqlalchemy import and_, or_
        from app.infrastructure.database.models.user import UserRole
        from app.infrastructure.database.models.skill import UserSkill, Skill

        stmt = select(User).where(
            User.role == UserRole.FREELANCER,
            User.is_active == True,
        )

        if min_rate is not None:
            stmt = stmt.where(User.hourly_rate >= min_rate)
        if max_rate is not None:
            stmt = stmt.where(User.hourly_rate <= max_rate)
        if q:
            stmt = stmt.where(
                or_(
                    User.full_name.ilike(f"%{q}%"),
                    User.bio.ilike(f"%{q}%"),
                )
            )
        if skill:
            stmt = stmt.join(UserSkill, UserSkill.user_id == User.id).join(
                Skill, Skill.id == UserSkill.skill_id
            ).where(Skill.name == skill.lower().strip())

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return [self._to_entity(u) for u in result.scalars().all()]
