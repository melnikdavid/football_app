import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    coach = "coach"
    support = "support"
    affiliate = "affiliate"
    user = "user"


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    banned = "banned"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.user, nullable=False)
    status: Mapped[UserStatus] = mapped_column(SAEnum(UserStatus), default=UserStatus.active, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    subscription: Mapped["Subscription"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    content_views: Mapped[list["ContentView"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    challenge_completions: Mapped[list["ChallengeCompletion"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    points: Mapped["UserPoints"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    ai_sessions: Mapped[list["AISession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    affiliate: Mapped["Affiliate"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications: Mapped[list["NotificationLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")
