from app.application.dto.auth import LoginRequest, TokenResponse
from app.application.interfaces.user_repository import IUserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token


class LoginUser:

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def execute(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user:
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User is inactive")

        hashed = await self.user_repo.get_hashed_password(data.email)
        if not verify_password(data.password, hashed):
            raise ValueError("Invalid email or password")

        payload = {"sub": str(user.id), "role": user.role}

        return TokenResponse(
            access_token=create_access_token(payload),
            refresh_token=create_refresh_token(payload),
        )
