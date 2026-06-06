from fastapi import APIRouter, Depends, status
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.user import AddSkillsRequest, UserSkillsResponse
from app.application.use_cases.add_user_skills import AddUserSkills
from app.application.use_cases.get_user_skills import GetUserSkills
from app.application.use_cases.remove_user_skill import RemoveUserSkill
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.skill_repository import SkillRepository

router = APIRouter(prefix="/users", tags=["Skills"])


@router.post("/me/skills", summary="Add skills to my profile", response_model=UserSkillsResponse)
async def add_skills(
    data: AddSkillsRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = AddUserSkills(SkillRepository(db))
    return await use_case.execute(current_user.id, data)


@router.get("/me/skills", summary="Get my skills", response_model=UserSkillsResponse)
async def get_skills(
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetUserSkills(SkillRepository(db))
    return await use_case.execute(current_user.id)


@router.delete(
    "/me/skills/{skill_id}",
    summary="Remove skill from my profile",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_skill(
    skill_id: uuid.UUID,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = RemoveUserSkill(SkillRepository(db))
    await use_case.execute(current_user.id, skill_id)