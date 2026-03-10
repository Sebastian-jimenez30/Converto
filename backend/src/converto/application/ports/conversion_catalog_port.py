from abc import ABC, abstractmethod


class ConversionCatalogPort(ABC):
    @abstractmethod
    def list_supported_formats(self) -> dict[str, list[str]]:
        raise NotImplementedError

