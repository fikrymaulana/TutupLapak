# src/users/router.py
import logging
from fastapi import APIRouter, Depends,Body, status, HTTPException, Request
from sqlalchemy.orm import Session
from src.database import get_db
from .dependencies import CurrentUser, require_new_phone, require_new_email
from src.auth.models import User
from src.files.models import FileObject
from .schemas import UpdateProfileRequest, UserProfileResponse, LinkPhoneRequest, LinkEmailRequest
from . import service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["profile"])

def _resolve_file_public_info(db: Session, maybe_id: str | None):
    """
    Helper: terima internal UUID *atau* public fileId,
    balikan (public_id, uri, thumb) semuanya string.
    """
    public_id = ""
    uri = ""
    thumb = ""
    if not maybe_id:
        return public_id, uri, thumb

    f = db.query(FileObject).filter(FileObject.id == str(maybe_id)).first()
    if not f:
        f = db.query(FileObject).filter(FileObject.fileId == str(maybe_id)).first()
    if f:
        public_id = getattr(f, "fileId", "") or ""
        uri = getattr(f, "fileUri", "") or ""
        thumb = getattr(f, "fileThumbnailUri", "") or ""
    return public_id, uri, thumb


@router.get("/user", response_model=UserProfileResponse)
def get_profile(
    current_user: CurrentUser,       # ✅ gunakan dependency yang sudah kamu definisikan
    db: Session = Depends(get_db),
):
    """
    GET /v1/user
    - Return profile user yang sedang login
    - Semua field harus string ("" jika null)
    """
    prof = service.get_or_create_profile(db, current_user.id)

    file_public_id, file_uri, file_thumb = _resolve_file_public_info(db, prof.file_id)

    return {
        "email": current_user.email or "",
        "phone": current_user.phone or "",
        "fileId": file_public_id,
        "fileUri": file_uri,
        "fileThumbnailUri": file_thumb,
        "bankAccountName": prof.bank_account_name or "",
        "bankAccountHolder": prof.bank_account_holder or "",
        "bankAccountNumber": prof.bank_account_number or "",
    }
    



@router.put("/user", response_model=UserProfileResponse)
async def update_profile(
    request: Request,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    # --- VALIDASI 400 utk body jelek ---
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Bad Request")
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Bad Request")

    def _req_str_4_32(key: str) -> str:
        val = body.get(key, None)
        if not isinstance(val, str):
            raise HTTPException(status_code=400, detail="Bad Request")
        if not (4 <= len(val) <= 32):
            raise HTTPException(status_code=400, detail="Bad Request")
        return val

    bank_name   = _req_str_4_32("bankAccountName")
    bank_holder = _req_str_4_32("bankAccountHolder")
    bank_number = _req_str_4_32("bankAccountNumber")


    new_file_id = None
    
    keep_existing = True
    if "fileId" in body:
        keep_existing = False
        file_id_val = body.get("fileId")
        if not isinstance(file_id_val, str):
            raise HTTPException(status_code=400, detail="Bad Request")
        file_id_val = file_id_val.strip()
        if file_id_val == "":
            raise HTTPException(status_code=400, detail="Bad Request")
        new_file_id = file_id_val

    existing_prof = service.get_or_create_profile(db, current_user.id)
    prof = service.update_profile(
        db, current_user,
        file_id=(new_file_id if "fileId" in body else existing_prof.file_id),
        bank_name=bank_name,
        bank_holder=bank_holder,
        bank_number=bank_number,
    )

    public_id, file_uri, file_thumb = _resolve_file_public_info(db, prof.file_id)

    return {
        "email": current_user.email or "",
        "phone": current_user.phone or "",
        "fileId": public_id or "",              # string (boleh kosong)
        "fileUri": file_uri or "",              # string (boleh kosong)
        "fileThumbnailUri": file_thumb or "",   # string (boleh kosong)
        "bankAccountName": prof.bank_account_name or "",
        "bankAccountHolder": prof.bank_account_holder or "",
        "bankAccountNumber": prof.bank_account_number or "",
    }



@router.post("/user/link/phone", response_model=UserProfileResponse)
async def link_phone(
    current_user: CurrentUser,                 # 401 kalau no token
    phone: str = Depends(require_new_phone),  # 400/409 dari dependency
    db: Session = Depends(get_db),
):
    user = service.link_phone(current_user, phone, db)
    prof = service.get_or_create_profile(db, user.id)
    public_id, uri, thumb = _resolve_file_public_info(db, prof.file_id)
    return {
        "email": user.email or "",
        "phone": user.phone or "",
        "fileId": public_id or "",
        "fileUri": uri or "",
        "fileThumbnailUri": thumb or "",
        "bankAccountName": prof.bank_account_name or "",
        "bankAccountHolder": prof.bank_account_holder or "",
        "bankAccountNumber": prof.bank_account_number or "",
    }

@router.post("/user/link/email", response_model=UserProfileResponse)
async def link_email(
    current_user: CurrentUser,
    email: str = Depends(require_new_email),
    db: Session = Depends(get_db),
):
    user = service.link_email(current_user, email, db)
    prof = service.get_or_create_profile(db, user.id)
    public_id, uri, thumb = _resolve_file_public_info(db, prof.file_id)
    return {
        "email": user.email or "",
        "phone": user.phone or "",
        "fileId": public_id or "",
        "fileUri": uri or "",
        "fileThumbnailUri": thumb or "",
        "bankAccountName": prof.bank_account_name or "",
        "bankAccountHolder": prof.bank_account_holder or "",
        "bankAccountNumber": prof.bank_account_number or "",
    }