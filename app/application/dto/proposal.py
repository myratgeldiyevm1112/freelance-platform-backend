import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.infrastructure.database.models.proposal import ProposalStatus


class SubmitProposalRequest(BaseModel):
    cover_letter: str
    proposed_rate: Decimal


class ProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    freelancer_id: uuid.UUID
    cover_letter: str
    proposed_rate: Decimal
    status: ProposalStatus
    created_at: datetime
