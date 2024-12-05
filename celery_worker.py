import logging
from datetime import timedelta

from celery import Celery
from celery.schedules import schedule
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

from tasks import process_work_responses


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)


celery = Celery(
    "work_crm_connector",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

celery.conf.update(
    task_routes={
        "tasks.process_work_responses": {"queue": "work"},
    },
    beat_schedule={
        "process-work-responses-every-minute": {
            "task": "tasks.process_work_responses",
            "schedule": schedule(run_every=timedelta(seconds=60)),
        },
    },
    worker_max_tasks_per_child=1,
    worker_concurrency=1,
    timezone="UTC",
)
