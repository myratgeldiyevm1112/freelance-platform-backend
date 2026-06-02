import uuid
from pydantic import BaseModel, Field
from datetime import datetime

class LeaveReviewRequest(BaseModel):
    contract_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(None, max_length=1000)

class ReviewResponse(BaseModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    reviewer_id: uuid.UUID
    reviewee_id: uuid.UUID
    rating: int
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
