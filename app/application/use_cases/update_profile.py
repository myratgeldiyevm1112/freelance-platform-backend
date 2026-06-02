from app.application.dto.auth import UserResponse
from app.application.dto.user import UpdateProfileRequest
from app.application.interfaces.user_repository import IUserRepository
from app.domain.entities.user import UserEntity


class UpdateProfile:

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def execute(self, user: UserEntity, data: UpdateProfileRequest) -> UserResponse:
        updated = await self.user_repo.update(user.id, data)
        return UserResponse.model_validate(updated)