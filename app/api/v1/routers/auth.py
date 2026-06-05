from fastapi import APIRouter, Depends, status, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies.db import get_db
from app.core.limiter import limiter
from app.api.dependencies.cache import get_redis
from app.application.dto.auth import RegisterRequest, UserResponse, TokenResponse, LoginRequest
from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.register_user import RegisterUser
from app.application.use_cases.refresh_token import RefreshToken
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.cache.token_store import TokenStore
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    use_case = RegisterUser(UserRepository(db))
    return await use_case.execute(data)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    use_case = LoginUser(UserRepository(db), TokenStore(redis))
    return await use_case.execute(data)


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    use_case = RefreshToken(UserRepository(db), TokenStore(redis))
    return await use_case.execute(data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: RefreshRequest,
    redis: Redis = Depends(get_redis),
):
    try:
        from app.core.security import decode_token
        payload = decode_token(data.refresh_token)
        user_id = payload.get("sub")
        await TokenStore(redis).delete(user_id)
    except ValueError:
        pass