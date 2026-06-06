from pydantic import BaseModel, ConfigDict, Field, field_validator
import uuid
from datetime import datetime
from app.infrastructure.database.models.user import UserRole


class UpdateProfileRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=200)
    bio: str | None = Field(None, max_length=1000)
    hourly_rate: float | None = Field(None, gt=0)

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip() if v else v


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    bio: str | None = None
    hourly_rate: float | None = None
    avatar_url: str | None = None
    portfolio_urls: list | None = None
    created_at: datetime


class UploadAvatarResponse(BaseModel):
    avatar_url: str


class UploadPortfolioResponse(BaseModel):
    portfolio_urls: list[str]


class AddSkillsRequest(BaseModel):
    skills: list[str] = Field(..., min_length=1, max_length=20)

    @field_validator("skills")
    @classmethod
    def normalize_skills(cls, v):
        return [s.lower().strip() for s in v if s.strip()]


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    skill_id: uuid.UUID
    skill_name: str


class UserSkillsResponse(BaseModel):
    skills: list[SkillResponse]