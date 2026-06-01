import enum
from sqlalchemy import String, Text, Numeric, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructure.database.base import BaseModel


class UserRole(str, enum.Enum):
    CLIENT = "client"
    FREELANCER = "freelancer"


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    hourly_rate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
