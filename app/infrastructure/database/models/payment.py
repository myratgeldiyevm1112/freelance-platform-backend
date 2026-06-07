import uuid
import enum
from sqlalchemy import Numeric, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.base import BaseModel


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"       # ожидает оплаты
    ESCROWED = "escrowed"     # деньги заморожены
    RELEASED = "released"     # переведено фрилансеру
    REFUNDED = "refunded"     # возврат клиенту
    FAILED = "failed"         # ошибка оплаты


class Payment(BaseModel):
    __tablename__ = "payments"

    contract_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False, unique=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    freelancer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    platform_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    freelancer_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING
    )
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_transfer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
