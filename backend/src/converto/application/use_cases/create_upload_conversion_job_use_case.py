from pathlib import Path
import re

from converto.application.commands.create_upload_conversion_job_command import (
    CreateUploadConversionJobCommand,
)
from converto.application.ports.conversion_catalog_port import ConversionCatalogPort
from converto.application.ports.file_storage_port import FileStoragePort
from converto.application.ports.job_dispatcher_port import JobDispatcherPort
from converto.domain.entities.conversion_job import ConversionJob
from converto.domain.repositories.conversion_job_repository import ConversionJobRepository


class CreateUploadConversionJobUseCase:
    IMAGE_FORMATS = {"jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"}
    OFFICE_FORMATS = {
        "pdf",
        "doc",
        "docx",
        "odt",
        "rtf",
        "txt",
        "html",
        "xls",
        "xlsx",
        "ods",
        "ppt",
        "pptx",
        "odp",
    }
    AV_FORMATS = {
        "mp3",
        "wav",
        "m4a",
        "aac",
        "ogg",
        "flac",
        "wma",
        "mpa",
        "mp4",
        "mov",
        "mkv",
        "webm",
        "avi",
    }

    def __init__(
        self,
        repository: ConversionJobRepository,
        job_dispatcher: JobDispatcherPort,
        file_storage: FileStoragePort,
        catalog: ConversionCatalogPort,
        max_upload_mb: int = 25,
    ) -> None:
        self._repository = repository
        self._job_dispatcher = job_dispatcher
        self._file_storage = file_storage
        self._catalog = catalog
        self._max_upload_bytes = max_upload_mb * 1024 * 1024

    def execute(self, command: CreateUploadConversionJobCommand) -> ConversionJob:
        if not command.file_bytes:
            raise ValueError("Uploaded file is empty")
        if len(command.file_bytes) > self._max_upload_bytes:
            raise ValueError(f"File exceeds max size of {self._max_upload_bytes // (1024 * 1024)}MB")

        source_filename = self._sanitize_filename(command.source_filename)
        source_format = self._extract_extension(source_filename)
        target_format = command.target_format.strip().lower()
        self._validate_target_format(target_format)
        self._validate_conversion_pair(source_format, target_format)

        job = ConversionJob.create(
            source_filename=source_filename,
            source_format=source_format,
            target_format=target_format,
            source_key=f"inputs/{source_filename}",
        )
        job.source_key = f"inputs/{job.id}/{source_filename}"

        self._file_storage.upload_bytes(
            key=job.source_key,
            content=command.file_bytes,
            content_type=command.content_type,
        )

        saved = self._repository.save(job)
        self._job_dispatcher.dispatch_conversion(saved.id)
        return saved

    def _validate_target_format(self, target_format: str) -> None:
        supported = set()
        for formats in self._catalog.list_supported_formats().values():
            supported.update(value.lower() for value in formats)
        if target_format not in supported:
            raise ValueError(f"Unsupported target format: {target_format}")

    def _validate_conversion_pair(self, source_format: str, target_format: str) -> None:
        if source_format == target_format:
            return
        if source_format in self.IMAGE_FORMATS and target_format in self.IMAGE_FORMATS.union({"pdf"}):
            return
        if source_format in self.OFFICE_FORMATS and target_format in self.OFFICE_FORMATS:
            return
        if source_format in self.AV_FORMATS and target_format in self.AV_FORMATS:
            return
        raise ValueError(f"Unsupported conversion pair: {source_format} -> {target_format}")

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        base_name = Path(filename).name.strip()
        if not base_name:
            raise ValueError("Invalid filename")
        sanitized = re.sub(r"[^A-Za-z0-9._-]", "_", base_name)
        if "." not in sanitized:
            raise ValueError("File must include an extension")
        return sanitized

    @staticmethod
    def _extract_extension(filename: str) -> str:
        extension = Path(filename).suffix.lower().lstrip(".")
        if not extension:
            raise ValueError("Could not determine source format")
        return extension
