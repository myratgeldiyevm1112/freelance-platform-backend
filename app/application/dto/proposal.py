import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.infrastructure.database.models.proposal import ProposalStatus


class SubmitProposalRequest(BaseModel):
    cover_letter: str = Field(..., min_length=10, max_length=2000)
    proposed_rate: Decimal = Field(..., gt=0)


class ProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    freelancer_id: uuid.UUID
    cover_letter: str
    proposed_rate: Decimal
    status: ProposalStatus
    created_at: datetime

class UpdateProposalStatusRequest(BaseModel):
    status: ProposalStatus


class AcceptProposalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    proposal: ProposalResponse
    contract_id: uuid.UUID
