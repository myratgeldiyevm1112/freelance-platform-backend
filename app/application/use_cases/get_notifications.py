import uuid
from app.application.interfaces.notification_repository import INotificationRepository
from app.domain.entities.notification import NotificationEntity
from app.domain.entities.user import UserEntity


class GetNotifications:
    def __init__(self, notification_repo: INotificationRepository):
        self.notification_repo = notification_repo

    async def execute(
        self, current_user: UserEntity, limit: int = 20, offset: int = 0
    ) -> list[NotificationEntity]:
        return await self.notification_repo.get_by_user_id(
            current_user.id, limit=limit, offset=offset
        )


class MarkNotificationRead:
    def __init__(self, notification_repo: INotificationRepository):
        self.notification_repo = notification_repo

    async def execute(
        self, notification_id: uuid.UUID, current_user: UserEntity
    ) -> NotificationEntity:
        return await self.notification_repo.mark_as_read(notification_id, current_user.id)


class MarkAllNotificationsRead:
    def __init__(self, notification_repo: INotificationRepository):
        self.notification_repo = notification_repo

    async def execute(self, current_user: UserEntity) -> dict:
        await self.notification_repo.mark_all_as_read(current_user.id)
        return {"message": "All notifications marked as read"}


class GetUnreadNotificationsCount:
    def __init__(self, notification_repo: INotificationRepository):
        self.notification_repo = notification_repo

    async def execute(self, current_user: UserEntity) -> dict:
        count = await self.notification_repo.get_unread_count(current_user.id)
        return {"unread_count": count}
