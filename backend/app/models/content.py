import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Enum as SAEnum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ContentType(str, enum.Enum):
    video = "video"
    zoom = "zoom"
    podcast = "podcast"
    challenge = "challenge"
    article = "article"


class Content(Base):
    __tablename__ = "content"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[ContentType] = mapped_column(SAEnum(ContentType), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    vimeo_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    topic_category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    is_free: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    views: Mapped[list["ContentView"]] = relationship(back_populates="content", cascade="all, delete-orphan")


class ContentView(Base):
    __tablename__ = "content_views"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("content.id", ondelete="CASCADE"), nullable=False, index=True)
    watched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completion_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    user: Mapped["User"] = relationship(back_populates="content_views")
    content: Mapped["Content"] = relationship(back_populates="views")
