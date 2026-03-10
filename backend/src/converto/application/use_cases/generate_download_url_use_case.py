from converto.application.ports.file_storage_port import FileStoragePort


class GenerateDownloadUrlUseCase:
    def __init__(self, file_storage: FileStoragePort) -> None:
        self._file_storage = file_storage

    def execute(self, key: str, expires_seconds: int = 3600) -> str:
        return self._file_storage.generate_download_url(key=key, expires_seconds=expires_seconds)

