import uuid
from app.application.dto.user import AddSkillsRequest, UserSkillsResponse, SkillResponse
from app.application.interfaces.skill_repository import ISkillRepository


class AddUserSkills:
    def __init__(self, skill_repo: ISkillRepository):
        self.skill_repo = skill_repo

    async def execute(self, user_id: uuid.UUID, data: AddSkillsRequest) -> UserSkillsResponse:
        entities = await self.skill_repo.add_skills_to_user(user_id, data.skills)
        return UserSkillsResponse(
            skills=[
                SkillResponse(id=e.id, skill_id=e.skill_id, skill_name=e.skill_name)
                for e in entities
            ]
        )