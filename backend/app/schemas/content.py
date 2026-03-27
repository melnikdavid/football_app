import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.content import ContentType


class ContentOut(BaseModel):
    id: uuid.UUID
    type: ContentType
    title: str
    description: str | None
    vimeo_id: str | None
    thumbnail_url: str | None
    duration_sec: int | None
    topic_category: str | None
    published_at: datetime | None
    is_free: bool

    model_config = {"from_attributes": True}


class ContentViewIn(BaseModel):
    completion_pct: float
