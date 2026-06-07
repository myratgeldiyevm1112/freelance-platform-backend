import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.db import get_db
from app.application.dto.notification import NotificationResponse, UnreadCountResponse
from app.application.use_cases.get_notifications import (
    GetNotifications,
    MarkNotificationRead,
    MarkAllNotificationsRead,
    GetUnreadNotificationsCount,
)
from app.domain.entities.user import UserEntity
from app.infrastructure.repositories.notification_repository import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=list[NotificationResponse])
async def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetNotifications(NotificationRepository(db))
    return await use_case.execute(current_user, limit=limit, offset=offset)


@router.get("/unread", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = GetUnreadNotificationsCount(NotificationRepository(db))
    return await use_case.execute(current_user)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: uuid.UUID,
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = MarkNotificationRead(NotificationRepository(db))
    return await use_case.execute(notification_id, current_user)


@router.patch("/read-all", status_code=200)
async def mark_all_as_read(
    current_user: UserEntity = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    use_case = MarkAllNotificationsRead(NotificationRepository(db))
    return await use_case.execute(current_user)
