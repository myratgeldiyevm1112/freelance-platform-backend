import uuid
from app.application.dto.user import UserSkillsResponse, SkillResponse
from app.application.interfaces.skill_repository import ISkillRepository


class GetUserSkills:
    def __init__(self, skill_repo: ISkillRepository):
        self.skill_repo = skill_repo

    async def execute(self, user_id: uuid.UUID) -> UserSkillsResponse:
        entities = await self.skill_repo.get_user_skills(user_id)
        return UserSkillsResponse(
            skills=[
                SkillResponse(id=e.id, skill_id=e.skill_id, skill_name=e.skill_name)
                for e in entities
            ]
        )