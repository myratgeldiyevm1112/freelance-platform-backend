import uuid
from dataclasses import dataclass
from datetime import datetime
from app.infrastructure.database.models.contract import ContractStatus


@dataclass
class ContractEntity:
    id: uuid.UUID
    job_id: uuid.UUID
    proposal_id: uuid.UUID
    client_id: uuid.UUID
    freelancer_id: uuid.UUID
    agreed_rate: float
    status: ContractStatus
    created_at: datetime
    updated_at: datetime | None = None
