from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "moadon",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.workers.retention_tasks",
        "app.workers.notification_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Jerusalem",
    enable_utc=True,
    task_track_started=True,
    worker_max_tasks_per_child=1000,
    beat_schedule={
        # Check for inactive users daily at 10:00 Israel time
        "check-inactive-users": {
            "task": "app.workers.retention_tasks.check_inactive_users",
            "schedule": crontab(hour=10, minute=0),
        },
        # Send monthly NPS survey on the 1st of each month
        "monthly-nps": {
            "task": "app.workers.retention_tasks.send_monthly_nps",
            "schedule": crontab(day_of_month=1, hour=9, minute=0),
        },
        # Check upcoming games and send pre-game reminders daily at 8:00
        "pre-game-reminders": {
            "task": "app.workers.notification_tasks.send_pre_game_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
    },
)
