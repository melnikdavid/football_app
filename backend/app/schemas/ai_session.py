import uuid
from datetime import datetime
from pydantic import BaseModel


class AIMessageIn(BaseModel):
    message: str


class AIMessageOut(BaseModel):
    role: str
    content: str


class AISessionOut(BaseModel):
    id: uuid.UUID
    messages: list[AIMessageOut]
    updated_at: datetime

    model_config = {"from_attributes": True}
