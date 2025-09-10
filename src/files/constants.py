import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

ALLOWED_MIME = {"image/jpeg", "image/png"}


@dataclass
class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/uploaddb",
    )

    # MinIO / S3-compatible
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "uploads")
    MINIO_PUBLIC_URL: Optional[str] = os.getenv("MINIO_PUBLIC_URL")

    # Constraints
    MAX_FILE_BYTES: int = int(os.getenv("MAX_FILE_BYTES", str(100 * 1024)))  # 100 KiB
    THUMB_MAX_BYTES: int = int(os.getenv("THUMB_MAX_BYTES", str(10 * 1024)))  # 10 KiB
    THUMB_MAX_WIDTH: int = int(os.getenv("THUMB_MAX_WIDTH", "320"))
    THUMB_MAX_HEIGHT: int = int(os.getenv("THUMB_MAX_HEIGHT", "320"))

    APP_NAME: str = os.getenv("APP_NAME", "UploadAPI")
