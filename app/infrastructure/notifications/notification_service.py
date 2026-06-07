import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.notification_repository import NotificationRepository
from app.infrastructure.database.models.notification import NotificationType
from app.infrastructure.websocket.manager import manager


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.repo = NotificationRepository(db)

    async def notify(
        self,
        user_id: uuid.UUID,
        type: NotificationType,
        title: str,
        message: str,
        related_id: uuid.UUID | None = None,
    ) -> None:
        notification = await self.repo.create(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            related_id=related_id,
        )
        await manager.send_to_user(
            str(user_id),
            "notification",
            {
                "id": str(notification.id),
                "type": type.value,
                "title": title,
                "message": message,
                "related_id": str(related_id) if related_id else None,
                "created_at": notification.created_at.isoformat(),
            },
        )
