from botocore.exceptions import ClientError
import boto3

from converto.application.ports.file_storage_port import FileStoragePort


class S3FileStorage(FileStoragePort):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: str,
        public_endpoint: str | None = None,
    ) -> None:
        self._bucket = bucket
        self._endpoint = endpoint.rstrip("/")
        self._public_endpoint = public_endpoint.rstrip("/") if public_endpoint else None
        self._client = boto3.client(
            "s3",
            endpoint_url=self._endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

    def ensure_bucket_exists(self) -> None:
        try:
            self._client.head_bucket(Bucket=self._bucket)
            return
        except ClientError:
            self._client.create_bucket(Bucket=self._bucket)

    def upload_bytes(self, key: str, content: bytes, content_type: str | None = None) -> None:
        extra: dict[str, str] = {}
        if content_type:
            extra["ContentType"] = content_type
        self._client.put_object(Bucket=self._bucket, Key=key, Body=content, **extra)

    def generate_download_url(self, key: str, expires_seconds: int = 3600) -> str:
        url = self._client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_seconds,
        )
        if self._public_endpoint:
            return url.replace(self._endpoint, self._public_endpoint, 1)
        return url
