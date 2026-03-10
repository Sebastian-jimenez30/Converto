from abc import ABC, abstractmethod


class FileConverterPort(ABC):
    @abstractmethod
    def convert(self, source_key: str, source_format: str, target_format: str) -> str:
        raise NotImplementedError

