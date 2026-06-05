import uuid
from abc import ABC, abstractmethod
from app.domain.entities.skill import SkillEntity, UserSkillEntity


class ISkillRepository(ABC):

    @abstractmethod
    async def get_or_create_skill(self, name: str) -> SkillEntity:
        raise NotImplementedError

    @abstractmethod
    async def add_skills_to_user(self, user_id: uuid.UUID, skill_names: list[str]) -> list[UserSkillEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_skills(self, user_id: uuid.UUID) -> list[UserSkillEntity]:
        raise NotImplementedError

    @abstractmethod
    async def remove_user_skill(self, user_id: uuid.UUID, skill_id: uuid.UUID) -> None:
        raise NotImplementedError