from celery import Celery

from converto_worker.adapters.converters.mock_converter import MockConverter
from converto_worker.application.use_cases.process_conversion_use_case import (
    ProcessConversionUseCase,
)
from converto_worker.config.settings import Settings

settings = Settings()

celery_app = Celery("converto-worker")
celery_app.conf.broker_url = settings.celery_broker_url
celery_app.conf.result_backend = settings.celery_result_backend

process_conversion_use_case = ProcessConversionUseCase(converter=MockConverter())

# Ensure task registration when the worker starts.
import converto_worker.tasks  # noqa: E402,F401
