import uuid
from dataclasses import dataclass
from datetime import datetime
from app.infrastructure.database.models.proposal import ProposalStatus


@dataclass
class ProposalEntity:
    id: uuid.UUID
    job_id: uuid.UUID
    freelancer_id: uuid.UUID
    cover_letter: str
    proposed_rate: float
    status: ProposalStatus
    created_at: datetime
    updated_at: datetime | None = None
