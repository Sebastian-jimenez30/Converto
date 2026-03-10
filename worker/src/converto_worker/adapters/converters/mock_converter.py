from converto_worker.application.ports.file_converter_port import FileConverterPort


class MockConverter(FileConverterPort):
    def convert(self, source_key: str, source_format: str, target_format: str) -> str:
        return f"{source_key.rsplit('.', 1)[0]}.{target_format}".replace("..", ".")

