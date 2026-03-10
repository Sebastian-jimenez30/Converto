from converto_worker.application.ports.file_converter_port import FileConverterPort


class MockConverter(FileConverterPort):
    def convert(self, source_content: bytes, source_format: str, target_format: str) -> bytes:
        # Placeholder converter: keeps bytes untouched while pipeline and storage are validated.
        return source_content
