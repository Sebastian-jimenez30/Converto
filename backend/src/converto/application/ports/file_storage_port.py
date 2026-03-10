from abc import ABC, abstractmethod


class FileStoragePort(ABC):
    @abstractmethod
    def ensure_bucket_exists(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def upload_bytes(self, key: str, content: bytes, content_type: str | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def generate_download_url(self, key: str, expires_seconds: int = 3600) -> str:
        raise NotImplementedError

