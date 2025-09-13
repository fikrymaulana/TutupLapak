from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from minio import Minio

from src.auth.dependencies import get_current_user
from .dependencies import get_minio_client, get_settings
from src.database import get_db
from .schemas import FileUploadResponse
from .service import upload_file_and_thumbnail
from .exceptions import BadRequestError, ServerError
from .utils import _validate_url

router = APIRouter(prefix="/v1", tags=["file"])


@router.post("/file", response_model=FileUploadResponse, status_code=200)
async def upload_file_endpoint(
    file: UploadFile = File(..., description="jpeg/jpg/png; max 100KiB"),
    db: Session = Depends(get_db),
    minio_client: Minio = Depends(get_minio_client),
    settings=Depends(get_settings),
    current_user=Depends(get_current_user),
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
