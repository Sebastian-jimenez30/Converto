from converto.application.ports.conversion_catalog_port import ConversionCatalogPort


class StaticConversionCatalog(ConversionCatalogPort):
    def list_supported_formats(self) -> dict[str, list[str]]:
        return {
            "image": ["jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"],
            "document": ["pdf", "doc", "docx", "odt", "rtf", "txt", "html"],
            "spreadsheet": ["xls", "xlsx", "ods"],
            "presentation": ["ppt", "pptx", "odp"],
            "audio": ["mp3", "wav", "m4a", "aac", "ogg", "flac", "wma", "mpa"],
            "video": ["mp4", "mov", "mkv", "webm", "avi"],
        }
