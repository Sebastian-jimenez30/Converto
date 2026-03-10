from uuid import UUID

from fastapi import APIRouter, HTTPException

from converto.application.commands.create_conversion_job_command import CreateConversionJobCommand
from converto.application.use_cases.create_conversion_job_use_case import CreateConversionJobUseCase
from converto.application.use_cases.get_conversion_job_use_case import GetConversionJobUseCase
from converto.application.use_cases.list_supported_formats_use_case import (
    ListSupportedFormatsUseCase,
)
from converto.domain.entities.conversion_job import ConversionJob

from .schemas import (
    ConversionJobResponse,
    CreateConversionJobRequest,
    HealthResponse,
    SupportedFormatsResponse,
)


def _to_response(job: ConversionJob) -> ConversionJobResponse:
    return ConversionJobResponse(
        id=job.id,
        source_filename=job.source_filename,
        source_format=job.source_format,
        target_format=job.target_format,
        status=job.status.value,
        source_key=job.source_key,
        result_key=job.result_key,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def build_router(
    create_job_use_case: CreateConversionJobUseCase,
    get_job_use_case: GetConversionJobUseCase,
    list_formats_use_case: ListSupportedFormatsUseCase,
) -> APIRouter:
    router = APIRouter()

    @router.get("/health", response_model=HealthResponse, tags=["System"])
    def healthcheck() -> HealthResponse:
        return HealthResponse(service="converto-api", status="ok")

    @router.post("/v1/jobs", response_model=ConversionJobResponse, tags=["Jobs"])
    def create_job(payload: CreateConversionJobRequest) -> ConversionJobResponse:
        created = create_job_use_case.execute(
            CreateConversionJobCommand(
                source_filename=payload.source_filename,
                source_format=payload.source_format,
                target_format=payload.target_format,
                source_key=payload.source_key,
            )
        )
        return _to_response(created)

    @router.get("/v1/jobs/{job_id}", response_model=ConversionJobResponse, tags=["Jobs"])
    def get_job(job_id: UUID) -> ConversionJobResponse:
        job = get_job_use_case.execute(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return _to_response(job)

    @router.get(
        "/v1/capabilities/formats",
        response_model=SupportedFormatsResponse,
        tags=["Capabilities"],
    )
    def list_formats() -> SupportedFormatsResponse:
        return SupportedFormatsResponse(formats=list_formats_use_case.execute())

    return router
