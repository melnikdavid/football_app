import uuid
from pydantic import BaseModel


class AffiliateStatsOut(BaseModel):
    id: uuid.UUID
    code: str
    commission_pct: float
    total_earned: float
    total_referrals: int
    converted_referrals: int

    model_config = {"from_attributes": True}
