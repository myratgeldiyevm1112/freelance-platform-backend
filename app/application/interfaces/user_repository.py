from abc import ABC, abstractmethod
from app.domain.entities.user import UserEntity


class IUserRepository(ABC):

    @abstractmethod
    async def create(self, entity: UserEntity, hashed_password: str) -> UserEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id) -> UserEntity | None:
        raise NotImplementedError
