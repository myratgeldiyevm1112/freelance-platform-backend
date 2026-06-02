import enum
import uuid
from sqlalchemy import Numeric, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.base import BaseModel


class ContractStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Contract(BaseModel):
    __tablename__ = "contracts"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    proposal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("proposals.id", ondelete="CASCADE"),
        nullable=False, unique=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    freelancer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    agreed_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus), nullable=False, default=ContractStatus.ACTIVE
    )

