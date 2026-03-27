from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.workers.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.user import User, UserStatus
from app.models.content import ContentView
from app.services.notification_service import send_push_notification, send_whatsapp, send_email
import asyncio


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.workers.retention_tasks.check_inactive_users")
def check_inactive_users():
    """Send retention message to users inactive for 7+ days."""
    return run_async(_check_inactive_users())


async def _check_inactive_users():
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User)
            .options(selectinload(User.profile))
            .where(
                User.status == UserStatus.active,
                User.last_login_at < cutoff,
            )
        )
        inactive_users = result.scalars().all()

    sent = 0
    for user in inactive_users:
        name = user.profile.full_name if user.profile else "ספורטאי"
        message = f"היי {name}! 💪 חסרת לנו. בוא להתאמן היום — התוכן החדש מחכה לך!"
        await send_email(
            user.email,
            "חסרת לנו במועדון הספורטאים",
            f"<p>{message}</p><a href='https://moadon-hasportaim.co.il'>כניסה לפלטפורמה</a>",
        )
        sent += 1

    return {"inactive_users_notified": sent}


@celery_app.task(name="app.workers.retention_tasks.send_monthly_nps")
def send_monthly_nps():
    """Send NPS survey on the 1st of each month."""
    return run_async(_send_monthly_nps())


async def _send_monthly_nps():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.status == UserStatus.active)
        )
        users = result.scalars().all()

    sent = 0
    for user in users:
        await send_email(
            user.email,
            "כמה אתה ממליץ על מועדון הספורטאים? (30 שניות)",
            "<p>דרג אותנו מ-0 עד 10 ועזור לנו להשתפר!</p>"
            "<a href='https://moadon-hasportaim.co.il/nps'>לשאלון הקצר</a>",
        )
        sent += 1

    return {"nps_emails_sent": sent}


@celery_app.task(name="app.workers.retention_tasks.check_churn_risk")
def check_churn_risk():
    """Flag users with < 20% avg completion over last 30 days."""
    return run_async(_check_churn_risk())


async def _check_churn_risk():
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User)
            .options(selectinload(User.content_views))
            .where(User.status == UserStatus.active)
        )
        users = result.scalars().all()

    at_risk = 0
    for user in users:
        recent_views = [v for v in user.content_views if v.watched_at >= cutoff]
        if recent_views:
            avg_completion = sum(v.completion_pct for v in recent_views) / len(recent_views)
            if avg_completion < 20.0:
                at_risk += 1
                # Trigger retention flow via notification
                await send_email(
                    user.email,
                    "יש לנו תוכן מיוחד בשבילך!",
                    "<p>שים לב — פספסת הרבה תוכן ב-30 הימים האחרונים. בוא נתקדם יחד!</p>"
                    "<a href='https://moadon-hasportaim.co.il'>לצפייה בתוכן</a>",
                )

    return {"churn_risk_users_notified": at_risk}
