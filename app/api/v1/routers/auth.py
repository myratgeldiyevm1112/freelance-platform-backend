from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.db import get_db
from app.application.dto.auth import RegisterRequest, UserResponse
from app.application.use_cases.register_user import RegisterUser
from app.infrastructure.repositories.user_repository import UserRepository
from app.application.dto.auth import LoginRequest, TokenResponse
from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.refresh_token import RefreshToken
from pydantic import BaseModel


class RefreshRequest(BaseModel):
    refresh_token: str


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    use_case = RegisterUser(UserRepository(db))
    try:
        return await use_case.execute(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    use_case = LoginUser(UserRepository(db))
    try:
        return await use_case.execute(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))



@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    use_case = RefreshToken(UserRepository(db))
    try:
        return await use_case.execute(data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))