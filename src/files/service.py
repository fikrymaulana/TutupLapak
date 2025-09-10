from io import BytesIO
from typing import Tuple
from minio import Minio
from minio.error import S3Error
from sqlalchemy.orm import Session

from .constants import Settings
from .exceptions import ServerError
from .models import FileObject
from .utils import (
    generate_cuid,
    normalize_mime,
    ensure_allowed_mime,
    read_limited,
    detect_image_format,
    make_thumbnail_jpeg_under_limit,
)


def _ext_from_mime(mime: str) -> str:
    return "jpg" if mime == "image/jpeg" else "png"


def _ensure_bucket(client: Minio, bucket: str):
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
    except Exception as e:
        raise ServerError(f"MinIO bucket check/create failed: {e}")


def upload_file_and_thumbnail(
    upload_file, db: Session, client: Minio, s: Settings
) -> Tuple[str, str, str]:
    if not s.MINIO_PUBLIC_URL:
        raise ServerError(
            "MINIO_PUBLIC_URL is not configured (required for public URLs)"
        )

    # 1) read limited bytes
    file_bytes = read_limited(upload_file, s.MAX_FILE_BYTES)

    # 2) validate mime by header (optional) and by content
    header_mime = normalize_mime(upload_file.content_type)
    if header_mime:
        ensure_allowed_mime(header_mime)
    _, detected_mime = detect_image_format(file_bytes)
    ensure_allowed_mime(detected_mime)

    # 3) generate ids & keys
    # - row_id: internal DB primary key
    # - file_id: public file identifier returned to client
    row_id = generate_cuid()
    file_id = generate_cuid()

    ext = _ext_from_mime(detected_mime)
    object_key = f"{file_id}.{ext}"
    thumb_key = f"{file_id}_thumb.jpg"

    # 4) ensure bucket exists
    _ensure_bucket(client, s.MINIO_BUCKET)

    # 5) upload original
    try:
        client.put_object(
            bucket_name=s.MINIO_BUCKET,
            object_name=object_key,
            data=BytesIO(file_bytes),
            length=len(file_bytes),
            content_type=detected_mime,
        )
    except S3Error as e:
        raise ServerError(f"Upload failed: {e}")
    except Exception as e:
        raise ServerError(f"Upload failed: {e}")

    # 6) create thumbnail and upload
    thumb_bytes = make_thumbnail_jpeg_under_limit(
        image_bytes=file_bytes,
        target_bytes=s.THUMB_MAX_BYTES,
        max_w=s.THUMB_MAX_WIDTH,
        max_h=s.THUMB_MAX_HEIGHT,
    )
    try:
        client.put_object(
            bucket_name=s.MINIO_BUCKET,
            object_name=thumb_key,
            data=BytesIO(thumb_bytes),
            length=len(thumb_bytes),
            content_type="image/jpeg",
        )
    except Exception as e:
        raise ServerError(f"Upload thumbnail failed: {e}")

    # 7) build public URLs BEFORE saving metadata (fixes unbound-variable error)
    base = s.MINIO_PUBLIC_URL.rstrip("/")
    file_url = f"{base}/{s.MINIO_BUCKET}/{object_key}"
    thumb_url = f"{base}/{s.MINIO_BUCKET}/{thumb_key}"

    # 8) save metadata — now includes internal id and public fileId
    rec = FileObject(
        id=row_id,
        fileId=file_id,
        fileUri=file_url,
        fileThumbnailUri=thumb_url,
    )
    db.add(rec)
    db.commit()

    # 9) return public identifier + URLs
    return file_id, file_url, thumb_url
