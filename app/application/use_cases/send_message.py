import uuid
from app.application.interfaces.message_repository import IMessageRepository
from app.domain.entities.message import MessageEntity
from app.domain.entities.user import UserEntity
from app.domain.exceptions import ValidationError


class SendMessage:
    def __init__(self, message_repo: IMessageRepository):
        self.message_repo = message_repo

    async def execute(
        self,
        current_user: UserEntity,
        receiver_id: uuid.UUID,
        content: str,
        contract_id: uuid.UUID | None = None,
    ) -> MessageEntity:
        if current_user.id == receiver_id:
            raise ValidationError("Cannot send message to yourself")
        if not content.strip():
            raise ValidationError("Message content cannot be empty")
        return await self.message_repo.create(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=content.strip(),
            contract_id=contract_id,
        )
