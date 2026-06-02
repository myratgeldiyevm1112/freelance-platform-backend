import uuid
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.infrastructure.database.models.job import JobStatus
from datetime import datetime

class CreateJobRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=5, max_length=5000)
    budget: Decimal = Field(..., gt=0)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    title: str
    description: str
    budget: Decimal
    status: JobStatus
    created_at: datetime