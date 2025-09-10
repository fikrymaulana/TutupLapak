from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from minio import Minio
from urllib.parse import urlparse
import pydantic as pyd
from pydantic import AnyUrl

from .dependencies import get_db, get_minio_client, get_settings
from .schemas import FileUploadResponse
from .service import upload_file_and_thumbnail
from .exceptions import BadRequestError, ServerError

router = APIRouter(prefix="/v1", tags=["file"])


def _is_valid_url_by_stdlib(u: str) -> bool:
    p = urlparse(u)
    return p.scheme in ("http", "https") and bool(p.netloc)


def _validate_url(u: str) -> None:
    type_adapter = getattr(pyd, "TypeAdapter", None)
    if type_adapter is not None:
        try:
            type_adapter(AnyUrl).validate_python(u)
            return
        except Exception as e:
            raise ValueError("Invalid URL (pydantic validation failed)") from e

    if not _is_valid_url_by_stdlib(u):
        raise ValueError("Invalid URL (basic parsing failed)")


@router.post("/file", response_model=FileUploadResponse, status_code=200)
async def upload_file_endpoint(
    file: UploadFile = File(..., description="jpeg/jpg/png; max 100KiB"),
    db: Session = Depends(get_db),
    minio_client: Minio = Depends(get_minio_client),
    settings=Depends(get_settings),
):
    try:
        file_id, file_url, thumb_url = upload_file_and_thumbnail(
            file, db, minio_client, settings
        )

        try:
            _validate_url(file_url)
            _validate_url(thumb_url)
        except ValueError:
            raise HTTPException(status_code=500, detail="Generated file URL is invalid")

        return FileUploadResponse(
            fileId=file_id, fileUri=file_url, fileThumbnailUri=thumb_url
        )
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ServerError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
