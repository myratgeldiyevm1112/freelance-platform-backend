import uuid
from dataclasses import dataclass
from datetime import datetime
from app.infrastructure.database.models.dispute import DisputeStatus


@dataclass
class DisputeEntity:
    id: uuid.UUID
    contract_id: uuid.UUID
    opened_by: uuid.UUID
    reason: str
    status: DisputeStatus
    created_at: datetime
    updated_at: datetime
    resolution_note: str | None = None
    resolved_by: uuid.UUID | None = None
