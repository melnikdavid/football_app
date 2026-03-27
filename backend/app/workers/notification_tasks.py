from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.workers.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.models.user import User, UserStatus
from app.models.profile import Profile
from app.services.notification_service import send_email, send_whatsapp, send_push_notification
import asyncio


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.workers.notification_tasks.send_pre_game_reminders")
def send_pre_game_reminders():
    """Send preparation reminders to athletes with a game in the next 24 hours."""
    return run_async(_send_pre_game_reminders())


async def _send_pre_game_reminders():
    now = datetime.now(timezone.utc)
    in_24h = now + timedelta(hours=24)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User)
            .join(Profile, Profile.user_id == User.id)
            .options(selectinload(User.profile))
            .where(
                User.status == UserStatus.active,
                Profile.next_game_date.between(now, in_24h),
            )
        )
        users = result.scalars().all()

    sent = 0
    for user in users:
        name = user.profile.full_name if user.profile else "ספורטאי"
        message = (
            f"היי {name}! 🏆 יש לך משחק מחר. "
            "הכן את הגוף שלך עם השינה, התזונה וההתחממות המומלצים. בהצלחה!"
        )
        await send_email(
            user.email,
            "המשחק שלך מחר — הכן את עצמך!",
            f"<p>{message}</p>"
            "<a href='https://moadon-hasportaim.co.il/content?category=pre-game'>לטיפים להכנה</a>",
        )
        sent += 1

    return {"pre_game_reminders_sent": sent}


@celery_app.task(name="app.workers.notification_tasks.send_welcome_sequence")
def send_welcome_sequence(user_id: str, user_email: str, user_name: str):
    """Day 1 welcome + onboarding email."""
    return run_async(_send_welcome(user_email, user_name))


async def _send_welcome(email: str, name: str):
    html = f"""
    <h2>ברוך הבא למועדון הספורטאים, {name}! 🎉</h2>
    <p>אנחנו שמחים שהצטרפת אלינו.</p>
    <p>הנה הצעדים הראשונים:</p>
    <ol>
      <li><a href="https://moadon-hasportaim.co.il/profile">השלם את הפרופיל שלך</a></li>
      <li><a href="https://moadon-hasportaim.co.il/content">גלה את התוכן שלנו</a></li>
      <li><a href="https://moadon-hasportaim.co.il/ai">שוחח עם היועץ האישי שלך</a></li>
    </ol>
    <p>השבוע הראשון הוא בחינם — תהנה!</p>
    """
    await send_email(email, f"ברוך הבא, {name}! 🏆", html)
