"""Search tasks — stub, implemented in Phase 1.3"""
from app.workers.celery_app import celery_app

@celery_app.task(name="app.workers.search_tasks.run_job_search")
def run_job_search(search_id: str):
    pass

