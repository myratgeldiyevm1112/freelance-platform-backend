import uuid
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.infrastructure.database.models.job import JobStatus
from datetime import datetime


class CreateJobRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5, max_length=5000)
    budget: Decimal = Field(..., gt=0)
    required_skills: list[str] | None = Field(None, max_length=20)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("required_skills")
    @classmethod
    def normalize_skills(cls, v):
        if v is None:
            return v
        return [s.lower().strip() for s in v if s.strip()]


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    title: str
    description: str
    budget: Decimal
    status: JobStatus
    created_at: datetime
    required_skills: list[str] | None = None