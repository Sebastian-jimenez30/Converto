from contextlib import asynccontextmanager

from celery import Celery
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from converto.adapters.db.base import Base
from converto.adapters.queue.celery_job_dispatcher import CeleryJobDispatcher
from converto.adapters.repositories.sqlalchemy_conversion_job_repository import (
    SqlAlchemyConversionJobRepository,
)
from converto.adapters.web.router import build_router
from converto.application.use_cases.create_conversion_job_use_case import (
    CreateConversionJobUseCase,
)
from converto.application.use_cases.get_conversion_job_use_case import GetConversionJobUseCase
from converto.config.settings import Settings


def create_app() -> FastAPI:
    settings = Settings()
    session_factory = _build_session_factory(settings.database_url)
    repository = SqlAlchemyConversionJobRepository(session_factory)

    celery_app = Celery("converto-api")
    celery_app.conf.broker_url = settings.celery_broker_url
    celery_app.conf.result_backend = settings.celery_result_backend
    dispatcher = CeleryJobDispatcher(celery_app)

    create_job_use_case = CreateConversionJobUseCase(repository, dispatcher)
    get_job_use_case = GetConversionJobUseCase(repository)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        Base.metadata.create_all(bind=engine)
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
    app.include_router(build_router(create_job_use_case, get_job_use_case))

    @app.get("/", tags=["System"])
    def root() -> dict[str, str]:
        return {"message": "Converto API running"}

    return app


def _build_session_factory(database_url: str):
    from converto.adapters.db.session import build_session_factory

    return build_session_factory(database_url)

