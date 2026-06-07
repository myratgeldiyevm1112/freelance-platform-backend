import uuid
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.message_repository import IMessageRepository
from app.domain.entities.message import MessageEntity
from app.infrastructure.database.models.message import Message


def _to_entity(m: Message) -> MessageEntity:
    return MessageEntity(
        id=m.id,
        sender_id=m.sender_id,
        receiver_id=m.receiver_id,
        content=m.content,
        is_read=m.is_read,
        created_at=m.created_at,
        updated_at=m.updated_at,
        contract_id=m.contract_id,
    )


class MessageRepository(IMessageRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        sender_id: uuid.UUID,
        receiver_id: uuid.UUID,
        content: str,
        contract_id: uuid.UUID | None = None,
    ) -> MessageEntity:
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            contract_id=contract_id,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return _to_entity(message)

    async def get_conversation(
        self,
        user1_id: uuid.UUID,
        user2_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MessageEntity]:
        stmt = (
            select(Message)
            .where(
                or_(
                    and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                    and_(Message.sender_id == user2_id, Message.receiver_id == user1_id),
                )
            )
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return [_to_entity(m) for m in result.scalars().all()]

    async def mark_as_read(self, receiver_id: uuid.UUID, sender_id: uuid.UUID) -> None:
        stmt = (
            select(Message)
            .where(
                Message.receiver_id == receiver_id,
                Message.sender_id == sender_id,
                not Message.is_read,
            )
        )
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        for m in messages:
            m.is_read = True
        await self.db.commit()

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count()).where(
            Message.receiver_id == user_id,
            Message.is_read.is_(False),
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def get_conversations(self, user_id: uuid.UUID) -> list[dict]:
        subq = (
            select(
                func.greatest(Message.sender_id, Message.receiver_id).label("user_a"),
                func.least(Message.sender_id, Message.receiver_id).label("user_b"),
                func.max(Message.created_at).label("last_message_at"),
            )
            .where(
                or_(Message.sender_id == user_id, Message.receiver_id == user_id)
            )
            .group_by("user_a", "user_b")
            .subquery()
        )
        stmt = (
            select(Message)
            .join(
                subq,
                and_(
                    func.greatest(Message.sender_id, Message.receiver_id) == subq.c.user_a,
                    func.least(Message.sender_id, Message.receiver_id) == subq.c.user_b,
                    Message.created_at == subq.c.last_message_at,
                ),
            )
            .order_by(Message.created_at.desc())
        )
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        return [
            {
                "interlocutor_id": str(m.receiver_id if m.sender_id == user_id else m.sender_id),
                "last_message": m.content,
                "last_message_at": m.created_at.isoformat(),
                "is_read": m.is_read,
            }
            for m in messages
        ]
