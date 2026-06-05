from app.application.dto.auth import LoginRequest, TokenResponse
from app.application.interfaces.user_repository import IUserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.domain.exceptions import ValidationError, ForbiddenError, UnauthorizedError
from app.infrastructure.cache.token_store import TokenStore


class LoginUser:
    def __init__(self, user_repo: IUserRepository, token_store: TokenStore):
        self.user_repo = user_repo
        self.token_store = token_store

    async def execute(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user:
            raise ValidationError("Invalid email or password")
        if not user.is_active:
            raise ForbiddenError("User is inactive")
        hashed = await self.user_repo.get_hashed_password(data.email)
        if not verify_password(data.password, hashed):
            raise UnauthorizedError("Invalid email or password")

        payload = {"sub": str(user.id), "role": user.role}
        refresh_token = create_refresh_token(payload)

        await self.token_store.save(str(user.id), refresh_token)

        return TokenResponse(
            access_token=create_access_token(payload),
            refresh_token=refresh_token,
        )