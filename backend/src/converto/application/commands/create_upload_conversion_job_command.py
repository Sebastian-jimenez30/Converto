from dataclasses import dataclass


@dataclass(frozen=True)
class CreateUploadConversionJobCommand:
    source_filename: str
    target_format: str
    file_bytes: bytes
    content_type: str | None = None

