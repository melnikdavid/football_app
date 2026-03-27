import uuid
from datetime import datetime, date
from pydantic import BaseModel
from app.models.challenge import ChallengeType, UserRank


class ChallengeOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    points: int
    start_date: date | None
    end_date: date | None
    type: ChallengeType
    image_url: str | None

    model_config = {"from_attributes": True}


class ChallengeCompleteIn(BaseModel):
    evidence_url: str | None = None


class UserPointsOut(BaseModel):
    total_points: int
    rank: UserRank

    model_config = {"from_attributes": True}
