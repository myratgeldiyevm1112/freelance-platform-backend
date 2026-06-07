import uuid
from abc import ABC, abstractmethod
from app.domain.entities.message import MessageEntity


class IMessageRepository(ABC):

    @abstractmethod
    async def create(self, sender_id: uuid.UUID, receiver_id: uuid.UUID, content: str, contract_id: uuid.UUID | None) -> MessageEntity:
        pass

    @abstractmethod
    async def get_conversation(self, user1_id: uuid.UUID, user2_id: uuid.UUID, limit: int, offset: int) -> list[MessageEntity]:
        pass

    @abstractmethod
    async def mark_as_read(self, receiver_id: uuid.UUID, sender_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        pass

    @abstractmethod
    async def get_conversations(self, user_id: uuid.UUID) -> list[dict]:
        pass
