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
# tommy tambah import
from src.users import service as users_service  # NEW
from src.files.models import FileObject         # NEW  (perlu untuk resolve id internal)

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
        # NOTE: fungsi ini ternyata return PUBLIC id (files."fileId"), bukan internal id (files.id)
        file_id_public, file_url, thumb_url = upload_file_and_thumbnail(  # tommy: rename supaya jelas
            file, db, minio_client, settings
        )

        try:
            _validate_url(file_url)
            _validate_url(thumb_url)
        except ValueError:
            raise HTTPException(status_code=500, detail="Generated file URL is invalid")

        # --- NEW (tommy): resolve ke INTERNAL id (files.id) dari PUBLIC id (files."fileId") ---
        rec = db.query(FileObject).filter(FileObject.fileId == str(file_id_public)).first()  # NEW
        if not rec:  # NEW
            raise HTTPException(status_code=500, detail="Uploaded file not found after save")  # NEW
        file_id_internal = rec.id  # NEW
        # --- END NEW ---

        # --- NEW (tommy): link-kan ke profile dengan INTERNAL id (UUID) agar bisa FK & join cepat ---
        prof = users_service.get_or_create_profile(db, current_user.id)  # NEW
        prof.file_id = str(file_id_internal)  # NEW: selalu overwrite ke file terbaru
        db.add(prof)                          # NEW
        db.commit()                           # NEW
        db.refresh(prof)                      # NEW
        # --- END NEW ---

        # balas ke FE pakai PUBLIC id (tidak expose UUID internal)
        return FileUploadResponse(
            fileId=str(file_id_public),       # tommy: kirim public id ke FE
            fileUri=file_url,
            fileThumbnailUri=thumb_url,
        )

    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ServerError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
