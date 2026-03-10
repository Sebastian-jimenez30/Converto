from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    service: str
    status: str


class CreateConversionJobRequest(BaseModel):
    source_filename: str = Field(min_length=1, max_length=255)
    source_format: str = Field(min_length=1, max_length=40)
    target_format: str = Field(min_length=1, max_length=40)
    source_key: str = Field(min_length=1, max_length=512)


class ConversionJobResponse(BaseModel):
    id: UUID
    source_filename: str
    source_format: str
    target_format: str
    status: str
    source_key: str
    result_key: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class SupportedFormatsResponse(BaseModel):
    formats: dict[str, list[str]]
