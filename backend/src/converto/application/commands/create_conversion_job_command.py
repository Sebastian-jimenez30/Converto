from dataclasses import dataclass


@dataclass(frozen=True)
class CreateConversionJobCommand:
    source_filename: str
    source_format: str
    target_format: str
    source_key: str

