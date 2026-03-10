from celery import Celery
import time

from converto_worker.adapters.converters.mock_converter import MockConverter
from converto_worker.adapters.db.session import build_session_factory
from converto_worker.adapters.storage.s3_storage import S3Storage
from converto_worker.application.use_cases.process_conversion_use_case import (
    ProcessConversionUseCase,
)
from converto_worker.config.settings import Settings

settings = Settings()

celery_app = Celery("converto-worker")
celery_app.conf.broker_url = settings.celery_broker_url
celery_app.conf.result_backend = settings.celery_result_backend

process_conversion_use_case = ProcessConversionUseCase(converter=MockConverter())
session_factory = build_session_factory(settings.database_url)
s3_storage = S3Storage(
    endpoint=settings.s3_endpoint,
    access_key=settings.s3_access_key,
    secret_key=settings.s3_secret_key,
    bucket=settings.s3_bucket,
    region=settings.s3_region,
)
for attempt in range(15):
    try:
        s3_storage.ensure_bucket_exists()
        break
    except Exception:  # noqa: BLE001
        if attempt == 14:
            raise
        time.sleep(2)

# Ensure task registration when the worker starts.
import converto_worker.tasks  # noqa: E402,F401
