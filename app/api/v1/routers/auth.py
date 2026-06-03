from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.db import get_db
from app.application.dto.auth import RegisterRequest, UserResponse, TokenResponse, LoginRequest
from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.register_user import RegisterUser
from app.application.use_cases.refresh_token import RefreshToken
from app.infrastructure.repositories.user_repository import UserRepository
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    use_case = RegisterUser(UserRepository(db))
    return await use_case.execute(data)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    use_case = LoginUser(UserRepository(db))
    return await use_case.execute(data)


class RefreshRequest(BaseModel): 
    refresh_token: str


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    use_case = RefreshToken(UserRepository(db))
    return await use_case.execute(data.refresh_token)