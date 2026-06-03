from app.application.dto.auth import TokenResponse
from app.application.interfaces.user_repository import IUserRepository
from app.core.security import decode_token, create_access_token, create_refresh_token
from app.domain.exceptions import ValidationError, NotFoundError, ForbiddenError


class RefreshToken:

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def execute(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except ValueError:
            raise ValidationError("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise ValidationError("Invalid token type")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        if not user.is_active:
            raise ForbiddenError("User is inactive")

        new_payload = {"sub": str(user.id), "role": user.role}

        return TokenResponse(
            access_token=create_access_token(new_payload),
            refresh_token=create_refresh_token(new_payload),
        )
