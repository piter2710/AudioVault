from celery import Celery
from settings import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# Autodiscover tasks from the standard folders
# celery_app.autodiscover_tasks(["tasks", "services"])
