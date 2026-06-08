import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.infrastructure.database.models.dispute import DisputeStatus


class OpenDisputeRequest(BaseModel):
    contract_id: uuid.UUID
    reason: str = Field(..., min_length=10, max_length=1000)


class ResolveDisputeRequest(BaseModel):
    resolution: str = Field(..., pattern="^(refund|release)$")
    resolution_note: str | None = Field(None, max_length=500)


class DisputeResponse(BaseModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    opened_by: uuid.UUID
    reason: str
    status: DisputeStatus
    resolution_note: str | None
    resolved_by: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
