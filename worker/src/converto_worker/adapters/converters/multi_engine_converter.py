from __future__ import annotations

from io import BytesIO
from pathlib import Path
import subprocess
import tempfile

from PIL import Image

from converto_worker.application.ports.file_converter_port import FileConverterPort


class MultiEngineConverter(FileConverterPort):
    IMAGE_FORMATS = {"jpg", "jpeg", "png", "webp", "bmp", "tiff", "gif"}
    OFFICE_FORMATS = {
        "pdf",
        "doc",
        "docx",
        "odt",
        "rtf",
        "txt",
        "html",
        "xls",
        "xlsx",
        "ods",
        "ppt",
        "pptx",
        "odp",
    }
    AV_FORMATS = {
        "mp3",
        "wav",
        "m4a",
        "aac",
        "ogg",
        "flac",
        "wma",
        "mpa",
        "mp4",
        "mov",
        "mkv",
        "webm",
        "avi",
    }

    def convert(self, source_content: bytes, source_format: str, target_format: str) -> bytes:
        source = source_format.lower()
        target = target_format.lower()

        if source == target:
            return source_content

        if source in self.IMAGE_FORMATS and target in self.IMAGE_FORMATS.union({"pdf"}):
            return self._convert_with_pillow(source_content, target)

        if source in self.OFFICE_FORMATS and target in self.OFFICE_FORMATS:
            return self._convert_with_libreoffice(source_content, source, target)

        if source in self.AV_FORMATS and target in self.AV_FORMATS:
            return self._convert_with_ffmpeg(source_content, source, target)

        raise ValueError(f"Unsupported conversion pair: {source} -> {target}")

    def _convert_with_pillow(self, source_content: bytes, target: str) -> bytes:
        with Image.open(BytesIO(source_content)) as image:
            output = BytesIO()
            target_map = {
                "jpg": "JPEG",
                "jpeg": "JPEG",
                "png": "PNG",
                "webp": "WEBP",
                "bmp": "BMP",
                "tiff": "TIFF",
                "gif": "GIF",
                "pdf": "PDF",
            }
            target_name = target_map[target]
            image_to_save = image
            if target_name == "JPEG" and image.mode not in {"RGB", "L"}:
                image_to_save = image.convert("RGB")
            image_to_save.save(output, format=target_name)
            return output.getvalue()

    def _convert_with_ffmpeg(self, source_content: bytes, source: str, target: str) -> bytes:
        with tempfile.TemporaryDirectory(prefix="converto-av-") as temp_dir:
            input_path = Path(temp_dir) / f"input.{source}"
            output_path = Path(temp_dir) / f"output.{target}"
            input_path.write_bytes(source_content)

            command = [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                str(output_path),
            ]
            self._run_command(command, "FFmpeg conversion failed")
            if not output_path.exists():
                raise RuntimeError(f"FFmpeg did not produce output for {source} -> {target}")
            return output_path.read_bytes()

    def _convert_with_libreoffice(self, source_content: bytes, source: str, target: str) -> bytes:
        with tempfile.TemporaryDirectory(prefix="converto-doc-") as temp_dir:
            temp_path = Path(temp_dir)
            input_path = temp_path / f"input.{source}"
            input_path.write_bytes(source_content)

            command = [
                "soffice",
                "--headless",
                "--nologo",
                "--nodefault",
                "--nofirststartwizard",
                "--nolockcheck",
                "--convert-to",
                target,
                "--outdir",
                str(temp_path),
                str(input_path),
            ]
            self._run_command(command, "LibreOffice conversion failed")

            expected = temp_path / f"{input_path.stem}.{target}"
            if expected.exists():
                return expected.read_bytes()

            candidates = list(temp_path.glob(f"{input_path.stem}.*"))
            if not candidates:
                raise RuntimeError(f"LibreOffice did not produce output for {source} -> {target}")
            return candidates[0].read_bytes()

    @staticmethod
    def _run_command(command: list[str], failure_message: str) -> None:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() or "no stderr"
            raise RuntimeError(f"{failure_message}: {stderr}")

