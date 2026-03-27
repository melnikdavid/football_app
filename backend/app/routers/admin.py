from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models.user import User, UserStatus
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionPlan
from app.middleware.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def get_dashboard(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    thirty_days_ago = now - timedelta(days=30)

    total_users = await db.execute(select(func.count(User.id)))
    active_subs = await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.status.in_([SubscriptionStatus.active, SubscriptionStatus.trialing])
        )
    )
    monthly_subs = await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.plan == SubscriptionPlan.monthly,
            Subscription.status == SubscriptionStatus.active,
        )
    )
    new_users_30d = await db.execute(
        select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
    )
    cancelled_30d = await db.execute(
        select(func.count(Subscription.id)).where(
            Subscription.cancelled_at >= thirty_days_ago
        )
    )

    monthly_count = monthly_subs.scalar() or 0
    mrr = monthly_count * 269.0

    return {
        "total_users": total_users.scalar() or 0,
        "active_subscriptions": active_subs.scalar() or 0,
        "mrr_ils": mrr,
        "new_users_last_30d": new_users_30d.scalar() or 0,
        "cancellations_last_30d": cancelled_30d.scalar() or 0,
    }
