import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "ArkaMarket.settings"
)

app=Celery("ArkaMarket")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)
app.autodiscover_tasks()

app.conf.beat_schedule={
    "cancel-expired-orders":{
        "task":
    "order.tasks.cancel_expired_orders",
        "schedule":crontab(minute=0),
    },
}