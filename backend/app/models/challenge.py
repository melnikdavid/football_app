import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, Enum as SAEnum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ChallengeType(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    seasonal = "seasonal"


class UserRank(str, enum.Enum):
    bronze = "bronze"
    silver = "silver"
    gold = "gold"
    champion = "champion"


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    type: Mapped[ChallengeType] = mapped_column(SAEnum(ChallengeType), nullable=False, index=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    completions: Mapped[list["ChallengeCompletion"]] = relationship(back_populates="challenge", cascade="all, delete-orphan")


class ChallengeCompletion(Base):
    __tablename__ = "challenge_completions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    challenge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    evidence_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship(back_populates="challenge_completions")
    challenge: Mapped["Challenge"] = relationship(back_populates="completions")


class UserPoints(Base):
    __tablename__ = "user_points"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rank: Mapped[UserRank] = mapped_column(SAEnum(UserRank), default=UserRank.bronze, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="points")
