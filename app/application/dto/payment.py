import uuid
from datetime import datetime
from pydantic import BaseModel
from app.infrastructure.database.models.payment import PaymentStatus


class CreatePaymentRequest(BaseModel):
    freelancer_id: uuid.UUID


class PaymentIntentResponse(BaseModel):
    payment_id: str
    client_secret: str
    amount: float
    platform_fee: float
    freelancer_amount: float


class PaymentResponse(BaseModel):
    id: uuid.UUID
    contract_id: uuid.UUID
    client_id: uuid.UUID
    freelancer_id: uuid.UUID
    amount: float
    platform_fee: float
    freelancer_amount: float
    status: PaymentStatus
    stripe_payment_intent_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
