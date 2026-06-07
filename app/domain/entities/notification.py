import uuid
from dataclasses import dataclass
from datetime import datetime
from app.infrastructure.database.models.notification import NotificationType


@dataclass
class NotificationEntity:
    id: uuid.UUID
    user_id: uuid.UUID
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime
    updated_at: datetime
    related_id: uuid.UUID | None = None
