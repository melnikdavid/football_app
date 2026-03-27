import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.subscription import SubscriptionPlan, SubscriptionStatus, PaymentProvider


class SubscriptionOut(BaseModel):
    id: uuid.UUID
    plan: SubscriptionPlan
    price: float
    status: SubscriptionStatus
    trial_end: datetime | None
    next_billing: datetime | None
    payment_provider: PaymentProvider | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StartTrialIn(BaseModel):
    payment_provider: PaymentProvider
    provider_token: str  # tokenized card / payment token from provider SDK
