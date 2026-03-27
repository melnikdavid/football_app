import uuid
from datetime import datetime
from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    age: int | None = None
    position: str | None = None
    team: str | None = None
    city: str | None = None
    weight: float | None = None
    height: float | None = None
    training_frequency: int | None = None
    goals: dict | None = None
    phone: str | None = None
    next_game_date: datetime | None = None


class ProfileOut(BaseModel):
    user_id: uuid.UUID
    full_name: str
    age: int | None
    position: str | None
    team: str | None
    city: str | None
    weight: float | None
    height: float | None
    training_frequency: int | None
    goals: dict | None
    avatar_url: str | None
    phone: str | None
    next_game_date: datetime | None
    updated_at: datetime

    model_config = {"from_attributes": True}
