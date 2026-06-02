from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.auth import UserResponse
from app.application.dto.user import UpdateProfileRequest
from app.application.use_cases.update_profile import UpdateProfile
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserEntity = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UpdateProfileRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = UpdateProfile(UserRepository(db))
    return await use_case.execute(current_user, data)
