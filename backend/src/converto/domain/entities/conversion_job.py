from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from uuid import UUID, uuid4


class JobStatus(StrEnum):
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


@dataclass
class ConversionJob:
    id: UUID
    source_filename: str
    source_format: str
    target_format: str
    source_key: str
    status: JobStatus
    result_key: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        source_filename: str,
        source_format: str,
        target_format: str,
        source_key: str,
    ) -> "ConversionJob":
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            source_filename=source_filename,
            source_format=source_format,
            target_format=target_format,
            source_key=source_key,
            status=JobStatus.QUEUED,
            result_key=None,
            error_message=None,
            created_at=now,
            updated_at=now,
        )

