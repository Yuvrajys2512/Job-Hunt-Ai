"""
Celery application setup.

Celery is a distributed task queue. When FastAPI receives a request to
"search for 50 jobs", it doesn't run that work itself — it drops a
task message into Redis and immediately returns a task ID to the client.

A separate Celery worker process picks up that task from Redis and runs it.
The client polls (or receives WebSocket events) for progress updates.

This separation means:
- The API stays fast and responsive (never blocks on long work)
- Tasks can be retried automatically on failure
- You can scale workers independently of the API
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "jobhunt_ai",
    broker=settings.REDIS_URL,          # Redis as the message transport
    backend=settings.REDIS_URL,         # Redis to store task results
    include=[
        "app.workers.search_tasks",     # job search tasks
        "app.workers.apply_tasks",      # application submission tasks
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,

    # Retry policy: if a task fails, retry up to 3 times with 60s delay
    task_acks_late=True,               # only ack after successful completion
    task_reject_on_worker_lost=True,   # re-queue if worker dies mid-task

    # Task routing — different queues for different priority work
    task_routes={
        "app.workers.search_tasks.*": {"queue": "search"},
        "app.workers.apply_tasks.*":  {"queue": "apply"},
    },
)
