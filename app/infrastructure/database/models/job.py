from sqlalchemy import String, Text, Numeric, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.base import BaseModel
import enum
import uuid


class JobStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class Job(BaseModel):
    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_status", "status"),
        Index("ix_jobs_client_id", "client_id"),
        Index("ix_jobs_search_vector", "search_vector", postgresql_using="gin"),
    )

    client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    budget: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), nullable=False, default=JobStatus.OPEN
    )
    required_skills: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)