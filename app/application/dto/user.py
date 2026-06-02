from pydantic import BaseModel, ConfigDict
from app.infrastructure.database.models.user import UserRole


class UpdateProfileRequest(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    hourly_rate: float | None = None