from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus, PaymentProvider
from app.schemas.subscription import SubscriptionOut, StartTrialIn
from app.middleware.auth import get_current_user
from app.services.payment_service import create_stripe_trial_subscription, cancel_stripe_subscription
import stripe

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/me", response_model=SubscriptionOut)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Subscription).where(Subscription.user_id == current_user.id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")
    return sub


@router.post("/start-trial", response_model=SubscriptionOut, status_code=201)
async def start_trial(
    body: StartTrialIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(select(Subscription).where(Subscription.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Subscription already exists")

    if body.payment_provider == PaymentProvider.stripe:
        result = await create_stripe_trial_subscription(current_user.email, body.provider_token)
        trial_end = datetime.fromtimestamp(result["trial_end"], tz=timezone.utc) if result.get("trial_end") else None
        sub = Subscription(
            user_id=current_user.id,
            plan=SubscriptionPlan.trial,
            price=1.0,  # 1 ₪ for the first week
            status=SubscriptionStatus.trialing,
            trial_end=trial_end,
            payment_provider=PaymentProvider.stripe,
            provider_subscription_id=result["provider_subscription_id"],
            provider_customer_id=result["provider_customer_id"],
        )
    else:
        raise HTTPException(status_code=400, detail="Payment provider not yet supported in this region")

    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.post("/cancel", status_code=204)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Subscription).where(Subscription.user_id == current_user.id))
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")

    if sub.provider_subscription_id and sub.payment_provider == PaymentProvider.stripe:
        await cancel_stripe_subscription(sub.provider_subscription_id)

    sub.status = SubscriptionStatus.cancelled
    sub.cancelled_at = datetime.now(timezone.utc)
    await db.commit()


@router.post("/webhooks/payment")
async def payment_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, None)  # secret loaded from settings in payment_service
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "invoice.payment_succeeded":
        sub_id = event["data"]["object"]["subscription"]
        result = await db.execute(
            select(Subscription).where(Subscription.provider_subscription_id == sub_id)
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = SubscriptionStatus.active
            sub.plan = SubscriptionPlan.monthly
            sub.price = 269.0
            await db.commit()

    elif event["type"] == "customer.subscription.deleted":
        sub_id = event["data"]["object"]["id"]
        result = await db.execute(
            select(Subscription).where(Subscription.provider_subscription_id == sub_id)
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.status = SubscriptionStatus.cancelled
            await db.commit()

    return {"received": True}
