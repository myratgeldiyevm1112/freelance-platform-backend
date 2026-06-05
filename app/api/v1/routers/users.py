from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.auth import UserResponse
from app.application.dto.user import UpdateProfileRequest, UploadAvatarResponse, UploadPortfolioResponse
from app.application.use_cases.update_profile import UpdateProfile
from app.application.use_cases.upload_avatar import UploadAvatar
from app.application.use_cases.upload_portfolio import UploadPortfolio
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", summary="Get my profile", response_model=UserResponse)
async def get_me(current_user: UserEntity = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.patch("/me", summary="Update my profile", response_model=UserResponse)
async def update_me(
    data: UpdateProfileRequest,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = UpdateProfile(UserRepository(db))
    return await use_case.execute(current_user, data)


@router.post(
    "/me/avatar",
    summary="Upload profile avatar",
    description="JPG/PNG only, max 5MB",
    response_model=UploadAvatarResponse,
)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = UploadAvatar(UserRepository(db))
    url = await use_case.execute(current_user, file)
    return UploadAvatarResponse(avatar_url=url)


@router.post(
    "/me/portfolio",
    summary="Upload portfolio files",
    description="JPG/PNG/PDF only, max 5MB per file",
    response_model=UploadPortfolioResponse,
)
async def upload_portfolio(
    files: list[UploadFile] = File(...),
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = UploadPortfolio(UserRepository(db))
    urls = await use_case.execute(current_user, files)
    return UploadPortfolioResponse(portfolio_urls=urls)