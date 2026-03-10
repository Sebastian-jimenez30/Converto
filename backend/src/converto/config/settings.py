from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = "development"
    api_cors_origins: str = "http://localhost:5173"
    database_url: str = "postgresql+psycopg://converto:converto@localhost:5432/converto"
    redis_url: str = "redis://localhost:6379/0"

    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "converto-files"
    s3_region: str = "us-east-1"

    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

