from converto.application.ports.conversion_catalog_port import ConversionCatalogPort


class StaticConversionCatalog(ConversionCatalogPort):
    def list_supported_formats(self) -> dict[str, list[str]]:
        return {
            "image": ["jpg", "png", "webp"],
            "document": ["pdf", "docx", "txt"],
            "audio": ["mp3", "wav"],
            "video": ["mp4", "webm"],
        }

