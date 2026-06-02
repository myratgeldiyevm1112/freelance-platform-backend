import uuid
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.infrastructure.database.models.job import JobStatus


class CreateJobRequest(BaseModel):
    title: str
    description: str
    budget: Decimal


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    client_id: uuid.UUID
    title: str
    description: str
    budget: Decimal
    status: JobStatus
