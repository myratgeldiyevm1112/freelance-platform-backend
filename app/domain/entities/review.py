import uuid
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ReviewEntity:
    id: uuid.UUID
    contract_id: uuid.UUID
    reviewer_id: uuid.UUID
    reviewee_id: uuid.UUID
    rating: int
    created_at: datetime
    comment: str | None = None
