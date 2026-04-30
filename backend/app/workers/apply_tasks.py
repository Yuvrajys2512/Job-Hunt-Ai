"""Apply tasks — stub, implemented in Phase 1.4"""
from app.workers.celery_app import celery_app

@celery_app.task(name="app.workers.apply_tasks.submit_application")
def submit_application(application_id: str):
    pass

