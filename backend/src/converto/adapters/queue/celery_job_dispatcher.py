from uuid import UUID

from celery import Celery

from converto.application.ports.job_dispatcher_port import JobDispatcherPort


class CeleryJobDispatcher(JobDispatcherPort):
    def __init__(self, celery_app: Celery) -> None:
        self._celery_app = celery_app

    def dispatch_conversion(self, job_id: UUID) -> None:
        self._celery_app.send_task("converto_worker.tasks.process_conversion", args=[str(job_id)])

