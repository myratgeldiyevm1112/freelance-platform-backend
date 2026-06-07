import uuid
from dataclasses import dataclass
from datetime import datetime
from app.infrastructure.database.models.payment import PaymentStatus


@dataclass
class PaymentEntity:
    id: uuid.UUID
    contract_id: uuid.UUID
    client_id: uuid.UUID
    freelancer_id: uuid.UUID
    amount: float
    platform_fee: float
    freelancer_amount: float
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    stripe_payment_intent_id: str | None = None
    stripe_transfer_id: str | None = None
