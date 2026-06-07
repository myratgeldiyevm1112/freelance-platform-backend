import uuid
from abc import ABC, abstractmethod
from app.domain.entities.notification import NotificationEntity
from app.infrastructure.database.models.notification import NotificationType


class INotificationRepository(ABC):

    @abstractmethod
    async def create(
        self,
        user_id: uuid.UUID,
        type: NotificationType,
        title: str,
        message: str,
        related_id: uuid.UUID | None = None,
    ) -> NotificationEntity:
        pass

    @abstractmethod
    async def get_by_user_id(
        self, user_id: uuid.UUID, limit: int, offset: int
    ) -> list[NotificationEntity]:
        pass

    @abstractmethod
    async def mark_as_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> NotificationEntity:
        pass

    @abstractmethod
    async def mark_all_as_read(self, user_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        pass
