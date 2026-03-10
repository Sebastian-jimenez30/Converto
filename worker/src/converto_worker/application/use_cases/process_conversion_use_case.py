from converto_worker.application.ports.file_converter_port import FileConverterPort


class ProcessConversionUseCase:
    def __init__(self, converter: FileConverterPort) -> None:
        self._converter = converter

    def execute(self, source_key: str, source_format: str, target_format: str) -> str:
        return self._converter.convert(source_key, source_format, target_format)

