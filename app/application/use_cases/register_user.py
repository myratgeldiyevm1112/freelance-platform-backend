import uuid
from app.application.dto.auth import RegisterRequest, UserResponse
from app.application.interfaces.user_repository import IUserRepository
from app.core.security import hash_password
from app.domain.entities.user import UserEntity


class RegisterUser:

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def execute(self, data: RegisterRequest) -> UserResponse:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email already registered")

        entity = UserEntity(
            id=uuid.uuid4(),
            email=data.email,
            full_name=data.full_name,
            role=data.role,
            is_active=True,
            created_at=None,
        )

        created = await self.user_repo.create(entity, hash_password(data.password))
        return UserResponse.model_validate(created)
