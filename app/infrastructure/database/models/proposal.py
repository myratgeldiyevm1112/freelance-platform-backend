import enum
import uuid
from sqlalchemy import Text, Numeric, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.base import BaseModel


class ProposalStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Proposal(BaseModel):
    __tablename__ = "proposals"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    freelancer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    cover_letter: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_rate: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[ProposalStatus] = mapped_column(
        Enum(ProposalStatus),
        nullable=False,
        default=ProposalStatus.PENDING,
    )
