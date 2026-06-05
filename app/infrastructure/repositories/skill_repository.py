import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.skill_repository import ISkillRepository
from app.domain.entities.skill import SkillEntity, UserSkillEntity
from app.infrastructure.database.models.skill import Skill, UserSkill


class SkillRepository(ISkillRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _skill_to_entity(self, model: Skill) -> SkillEntity:
        return SkillEntity(
            id=model.id,
            name=model.name,
            created_at=model.created_at,
        )

    def _user_skill_to_entity(self, model: UserSkill, skill_name: str) -> UserSkillEntity:
        return UserSkillEntity(
            id=model.id,
            user_id=model.user_id,
            skill_id=model.skill_id,
            skill_name=skill_name,
            created_at=model.created_at,
        )

    async def get_or_create_skill(self, name: str) -> SkillEntity:
        name = name.lower().strip()
        result = await self.session.execute(select(Skill).where(Skill.name == name))
        skill = result.scalar_one_or_none()
        if not skill:
            skill = Skill(id=uuid.uuid4(), name=name)
            self.session.add(skill)
            await self.session.flush()
        return self._skill_to_entity(skill)

    async def add_skills_to_user(self, user_id: uuid.UUID, skill_names: list[str]) -> list[UserSkillEntity]:
        result = []
        for name in skill_names:
            skill_entity = await self.get_or_create_skill(name)

            # проверяем что такой user_skill ещё не существует
            existing = await self.session.execute(
                select(UserSkill).where(
                    UserSkill.user_id == user_id,
                    UserSkill.skill_id == skill_entity.id,
                )
            )
            if existing.scalar_one_or_none():
                continue

            user_skill = UserSkill(
                id=uuid.uuid4(),
                user_id=user_id,
                skill_id=skill_entity.id,
            )
            self.session.add(user_skill)
            await self.session.flush()
            result.append(self._user_skill_to_entity(user_skill, skill_entity.name))
        return result

    async def get_user_skills(self, user_id: uuid.UUID) -> list[UserSkillEntity]:
        result = await self.session.execute(
            select(UserSkill, Skill)
            .join(Skill, Skill.id == UserSkill.skill_id)
            .where(UserSkill.user_id == user_id)
        )
        return [
            self._user_skill_to_entity(us, skill.name)
            for us, skill in result.all()
        ]

    async def remove_user_skill(self, user_id: uuid.UUID, skill_id: uuid.UUID) -> None:
        result = await self.session.execute(
            select(UserSkill).where(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == skill_id,
            )
        )
        user_skill = result.scalar_one_or_none()
        if user_skill:
            await self.session.delete(user_skill)
            await self.session.flush()