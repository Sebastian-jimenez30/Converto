from converto_worker.application.ports.file_converter_port import FileConverterPort


class ProcessConversionUseCase:
    def __init__(self, converter: FileConverterPort) -> None:
        self._converter = converter

    def execute(self, source_content: bytes, source_format: str, target_format: str) -> bytes:
        return self._converter.convert(source_content, source_format, target_format)
