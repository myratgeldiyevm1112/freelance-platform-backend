import uuid
from app.application.interfaces.skill_repository import ISkillRepository


class RemoveUserSkill:
    def __init__(self, skill_repo: ISkillRepository):
        self.skill_repo = skill_repo

    async def execute(self, user_id: uuid.UUID, skill_id: uuid.UUID) -> None:
        await self.skill_repo.remove_user_skill(user_id, skill_id)