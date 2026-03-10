from converto.application.ports.conversion_catalog_port import ConversionCatalogPort


class ListSupportedFormatsUseCase:
    def __init__(self, catalog: ConversionCatalogPort) -> None:
        self._catalog = catalog

    def execute(self) -> dict[str, list[str]]:
        return self._catalog.list_supported_formats()

