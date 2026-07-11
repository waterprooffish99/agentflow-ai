import os
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "agentflow",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.follow_ups", 
        "app.tasks.ai_summarization",
        "app.tasks.growth_ops",
        "app.tasks.chat_tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300, # 5 minutes
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    broker_transport_options={"visibility_timeout": 3600},
)

# Enable eager execution in test environment
if os.environ.get("APP_ENV") == "test":
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )

if __name__ == "__main__":
    celery_app.start()
