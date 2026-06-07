import uuid
from app.application.interfaces.message_repository import IMessageRepository
from app.domain.entities.message import MessageEntity
from app.domain.entities.user import UserEntity


class GetMessages:
    def __init__(self, message_repo: IMessageRepository):
        self.message_repo = message_repo

    async def execute(
        self,
        current_user: UserEntity,
        interlocutor_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MessageEntity]:
        messages = await self.message_repo.get_conversation(
            user1_id=current_user.id,
            user2_id=interlocutor_id,
            limit=limit,
            offset=offset,
        )
        await self.message_repo.mark_as_read(
            receiver_id=current_user.id,
            sender_id=interlocutor_id,
        )
        return messages


class GetConversations:
    def __init__(self, message_repo: IMessageRepository):
        self.message_repo = message_repo

    async def execute(self, current_user: UserEntity) -> list[dict]:
        return await self.message_repo.get_conversations(current_user.id)


class GetUnreadCount:
    def __init__(self, message_repo: IMessageRepository):
        self.message_repo = message_repo

    async def execute(self, current_user: UserEntity) -> dict:
        count = await self.message_repo.get_unread_count(current_user.id)
        return {"unread_count": count}
