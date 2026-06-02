import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from app.infrastructure.database.models.contract import ContractStatus


class ContractResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    proposal_id: uuid.UUID
    client_id: uuid.UUID
    freelancer_id: uuid.UUID
    agreed_rate: Decimal
    status: ContractStatus
    created_at: datetime

    model_config = {"from_attributes": True}
