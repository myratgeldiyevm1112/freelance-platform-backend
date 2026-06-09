from app.application.dto.auth import TokenResponse
from app.application.interfaces.user_repository import IUserRepository
from app.core.security import decode_token, create_access_token, create_refresh_token
from app.domain.exceptions import ValidationError, NotFoundError, ForbiddenError, UnauthorizedError
from app.infrastructure.cache.token_store import TokenStore


class RefreshToken:
    def __init__(self, user_repo: IUserRepository, token_store: TokenStore):
        self.user_repo = user_repo
        self.token_store = token_store

    async def execute(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise ValidationError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise ValidationError("Invalid token type")

        user_id = payload.get("sub")

        stored_token = await self.token_store.get(user_id)
        if not stored_token or stored_token != refresh_token:
            raise UnauthorizedError("Refresh token expired or already used")

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        if not user.is_active:
            raise ForbiddenError("User is inactive")

        new_payload = {"sub": str(user.id), "role": user.role}
        new_refresh_token = create_refresh_token(new_payload)

        await self.token_store.save(user_id, new_refresh_token)

        return TokenResponse(
            access_token=create_access_token(new_payload),
            refresh_token=new_refresh_token,
        )