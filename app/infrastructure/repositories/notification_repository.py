import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.interfaces.notification_repository import INotificationRepository
from app.domain.entities.notification import NotificationEntity
from app.infrastructure.database.models.notification import Notification, NotificationType
from app.domain.exceptions import NotFoundError, ForbiddenError


def _to_entity(n: Notification) -> NotificationEntity:
    return NotificationEntity(
        id=n.id,
        user_id=n.user_id,
        type=n.type,
        title=n.title,
        message=n.message,
        is_read=n.is_read,
        created_at=n.created_at,
        updated_at=n.updated_at,
        related_id=n.related_id,
    )


class NotificationRepository(INotificationRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        type: NotificationType,
        title: str,
        message: str,
        related_id: uuid.UUID | None = None,
    ) -> NotificationEntity:
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            related_id=related_id,
        )
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return _to_entity(notification)

    async def get_by_user_id(
        self, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> list[NotificationEntity]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        return [_to_entity(n) for n in result.scalars().all()]

    async def mark_as_read(
        self, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> NotificationEntity:
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.db.execute(stmt)
        notification = result.scalar_one_or_none()
        if not notification:
            raise NotFoundError("Notification not found")
        if notification.user_id != user_id:
            raise ForbiddenError("Not your notification")
        notification.is_read = True
        await self.db.commit()
        await self.db.refresh(notification)
        return _to_entity(notification)

    async def mark_all_as_read(self, user_id: uuid.UUID) -> None:
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        result = await self.db.execute(stmt)
        notifications = result.scalars().all()
        for n in notifications:
            n.is_read = True
        await self.db.commit()

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count()).where(
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
