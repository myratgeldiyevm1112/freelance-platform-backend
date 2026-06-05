import uuid
from dataclasses import dataclass
from datetime import datetime
from app.infrastructure.database.models.user import UserRole


@dataclass
class UserEntity:
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    bio: str | None = None
    hourly_rate: float | None = None
    avatar_url: str | None = None
    portfolio_urls: list | None = None