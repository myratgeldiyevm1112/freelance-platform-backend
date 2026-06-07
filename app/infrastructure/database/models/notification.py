import enum
import uuid
from sqlalchemy import String, Text, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.base import BaseModel


class NotificationType(str, enum.Enum):
    PROPOSAL_SUBMITTED = "proposal_submitted"
    PROPOSAL_ACCEPTED = "proposal_accepted"
    PROPOSAL_REJECTED = "proposal_rejected"
    CONTRACT_COMPLETED = "contract_completed"
    CONTRACT_CANCELLED = "contract_cancelled"
    NEW_MESSAGE = "new_message"
    NEW_REVIEW = "new_review"
    PAYMENT_ESCROWED = "payment_escrowed"
    PAYMENT_RELEASED = "payment_released"
    PAYMENT_REFUNDED = "payment_refunded"


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    related_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
