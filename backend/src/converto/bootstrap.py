from contextlib import asynccontextmanager
import time

from celery import Celery
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from converto.adapters.db.base import Base
from converto.adapters.catalog.static_conversion_catalog import StaticConversionCatalog
from converto.adapters.queue.celery_job_dispatcher import CeleryJobDispatcher
from converto.adapters.repositories.sqlalchemy_conversion_job_repository import (
    SqlAlchemyConversionJobRepository,
)
from converto.adapters.storage.s3_file_storage import S3FileStorage
from converto.adapters.web.router import build_router
from converto.application.use_cases.create_conversion_job_use_case import (
    CreateConversionJobUseCase,
)
from converto.application.use_cases.create_upload_conversion_job_use_case import (
    CreateUploadConversionJobUseCase,
)
from converto.application.use_cases.generate_download_url_use_case import (
    GenerateDownloadUrlUseCase,
)
from converto.application.use_cases.get_conversion_job_use_case import GetConversionJobUseCase
from converto.application.use_cases.list_supported_formats_use_case import (
    ListSupportedFormatsUseCase,
)
from converto.config.settings import Settings


def create_app() -> FastAPI:
    settings = Settings()
    session_factory = _build_session_factory(settings.database_url)
    repository = SqlAlchemyConversionJobRepository(session_factory)

    celery_app = Celery("converto-api")
    celery_app.conf.broker_url = settings.celery_broker_url
    celery_app.conf.result_backend = settings.celery_result_backend
    dispatcher = CeleryJobDispatcher(celery_app)
    catalog = StaticConversionCatalog()
    file_storage = S3FileStorage(
        endpoint=settings.s3_endpoint,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        bucket=settings.s3_bucket,
        region=settings.s3_region,
        public_endpoint=settings.s3_public_endpoint,
    )

    create_job_use_case = CreateConversionJobUseCase(repository, dispatcher)
    create_upload_job_use_case = CreateUploadConversionJobUseCase(
        repository=repository,
        job_dispatcher=dispatcher,
        file_storage=file_storage,
        catalog=catalog,
        max_upload_mb=settings.max_upload_mb,
    )
    get_job_use_case = GetConversionJobUseCase(repository)
    list_formats_use_case = ListSupportedFormatsUseCase(catalog)
    generate_download_url_use_case = GenerateDownloadUrlUseCase(file_storage)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        Base.metadata.create_all(bind=engine)
        for attempt in range(15):
            try:
                file_storage.ensure_bucket_exists()
                break
            except Exception:  # noqa: BLE001
                if attempt == 14:
                    raise
                time.sleep(2)
        yield

    app = FastAPI(
        title="Converto API",
        version="0.1.0",
        description="Hexagonal backend for file conversion jobs.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.api_cors_origins.split(",")],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(
        build_router(
            create_job_use_case=create_job_use_case,
            create_upload_job_use_case=create_upload_job_use_case,
            get_job_use_case=get_job_use_case,
            list_formats_use_case=list_formats_use_case,
            generate_download_url_use_case=generate_download_url_use_case,
        )
    )

    @app.get("/", tags=["System"])
    def root() -> dict[str, str]:
        return {"message": "Converto API running"}

    return app


def _build_session_factory(database_url: str):
    from converto.adapters.db.session import build_session_factory

    return build_session_factory(database_url)
