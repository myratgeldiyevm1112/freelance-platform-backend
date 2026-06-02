import uuid
from dataclasses import dataclass
from datetime import datetime
from app.infrastructure.database.models.job import JobStatus


@dataclass
class JobEntity:
    id: uuid.UUID
    client_id: uuid.UUID
    title: str
    description: str
    budget: float
    status: JobStatus
    created_at: datetime
    updated_at: datetime | None = None
