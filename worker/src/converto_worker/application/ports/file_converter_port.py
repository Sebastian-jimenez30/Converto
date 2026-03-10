from abc import ABC, abstractmethod


class FileConverterPort(ABC):
    @abstractmethod
    def convert(self, source_content: bytes, source_format: str, target_format: str) -> bytes:
        raise NotImplementedError
