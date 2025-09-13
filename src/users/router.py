
from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.dependencies import get_current_user
from src.auth.models import User

from src.files.models import FileObject  # <- model files (kolom: fileId, fileUri, fileThumbnailUri)

from .schemas import UpdateProfileRequest, UserProfileResponse, LinkPhoneRequest, LinkEmailRequest
from . import service

router = APIRouter(prefix="/v1", tags=["profile"])

# @router.get("/user", response_model=UserProfileResponse)
# def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
#     prof = service.get_or_create_profile(db, current_user.id)
#     return {
#         "email": current_user.email or "",
#         "phone": current_user.phone or "",
#         "fileId": prof.file_id or "",
#         "fileUri": "",
#         "fileThumbnailUri": "",
#         "bankAccountName": prof.bank_account_name or "",
#         "bankAccountHolder": prof.bank_account_holder or "",
#         "bankAccountNumber": prof.bank_account_number or "",
#     }
@router.get("/user", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prof = service.get_or_create_profile(db, current_user.id)

    # default kosong sesuai kontrak
    file_public_id = ""
    file_uri = ""
    file_thumb = ""

    if prof.file_id:
        # 1) Lookup pakai INTERNAL id (UUID) yang disimpan di profiles.file_id
        f = db.query(FileObject).filter(FileObject.id == str(prof.file_id)).first()
        # 2) Backward-compat: kalau dulu sempat menyimpan public id di profiles.file_id
        if not f:
            f = db.query(FileObject).filter(FileObject.fileId == str(prof.file_id)).first()

        if f:
            # Ambil dari tabel files
            file_public_id = getattr(f, "fileId", "") or ""
            file_uri       = getattr(f, "fileUri", "") or ""
            file_thumb     = getattr(f, "fileThumbnailUri", "") or ""

    return {
        "email": current_user.email or "",
        "phone": current_user.phone or "",
        "fileId": file_public_id,          # <- dari tabel files (public id)
        "fileUri": file_uri,               # <- dari tabel files
        "fileThumbnailUri": file_thumb,    # <- dari tabel files

        "bankAccountName": prof.bank_account_name or "",
        "bankAccountHolder": prof.bank_account_holder or "",
        "bankAccountNumber": prof.bank_account_number or "",
    }

    

# @router.put("/user", response_model=UserProfileResponse)
# def update_profile(
#     body: UpdateProfileRequest,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     prof = service.update_profile(
#         db, current_user,
#         file_id=body.fileId,
#         bank_name=body.bankAccountName,
#         bank_holder=body.bankAccountHolder,
#         bank_number=body.bankAccountNumber,
#     )
#     return {
#         "email": current_user.email or "",
#         "phone": current_user.phone or "",
#         "fileId": prof.file_id or "",
#         "fileUri": "",
#         "fileThumbnailUri": "",
#         "bankAccountName": prof.bank_account_name or "",
#         "bankAccountHolder": prof.bank_account_holder or "",
#         "bankAccountNumber": prof.bank_account_number or "",
#     }

@router.put("/user", response_model=UserProfileResponse)
def update_profile(
    body: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # --- tommy NEW: ambil profil dulu (buat kalau belum ada) ---
    current_prof = service.get_or_create_profile(db, current_user.id)

    # --- tommy NEW: aturan update file ---
    # - body.fileId is None  -> JANGAN ubah file (pakai yang lama)
    # - body.fileId == ""    -> CLEAR file (set NULL)
    # - body.fileId ada isi  -> resolve (boleh public "fileId" atau internal "id") lalu simpan INTERNAL id
    if body.fileId is None:
        resolved_internal_id = current_prof.file_id  # keep existing
    elif body.fileId == "":
        resolved_internal_id = None  # clear
    else:
        needle = str(body.fileId).strip()
        f = (
            db.query(FileObject).filter(FileObject.id == needle).first() or
            db.query(FileObject).filter(FileObject.fileId == needle).first()
        )
        if not f:
            raise HTTPException(status_code=404, detail=f"file not found: {needle}")
        resolved_internal_id = str(f.id)  # simpan INTERNAL UUID

    # simpan ke profile via service (service-mu sudah handle field lain)
    prof = service.update_profile(
        db, current_user,
        file_id=resolved_internal_id,                 # <- simpan INTERNAL id (UUID) ke profiles.file_id

        bank_name=body.bankAccountName,
        bank_holder=body.bankAccountHolder,
        bank_number=body.bankAccountNumber,
    )


    # --- tommy NEW: bangun response ambil dari tabel files, bukan dari prof langsung ---
    file_public_id = ""
    file_uri = ""
    file_thumb = ""
    if prof.file_id:
        f2 = db.query(FileObject).filter(FileObject.id == str(prof.file_id)).first()
        if f2:
            file_public_id = getattr(f2, "fileId", "") or ""
            file_uri       = getattr(f2, "fileUri", "") or ""
            file_thumb     = getattr(f2, "fileThumbnailUri", "") or ""

    return {
        "email": current_user.email or "",
        "phone": current_user.phone or "",
        "fileId": file_public_id,       # kirim PUBLIC id ke FE
        "fileUri": file_uri,
        "fileThumbnailUri": file_thumb,

        "bankAccountName": prof.bank_account_name or "",
        "bankAccountHolder": prof.bank_account_holder or "",
        "bankAccountNumber": prof.bank_account_number or "",
    }

@router.post("/user/link/phone", status_code=status.HTTP_200_OK)
def link_phone(payload: LinkPhoneRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = service.link_phone(current_user, payload.phone, db)
    prof = service.get_or_create_profile(db, user.id)
    return {
        "email": user.email or "",
        "phone": user.phone or "",
        "fileId": prof.file_id or "",
        "fileUri": "",
        "fileThumbnailUri": "",
        "bankAccountName": prof.bank_account_name or "",
        "bankAccountHolder": prof.bank_account_holder or "",
        "bankAccountNumber": prof.bank_account_number or "",
    }

@router.post("/user/link/email", status_code=status.HTTP_200_OK)
def link_email(payload: LinkEmailRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = service.link_email(current_user, payload.email, db)
    prof = service.get_or_create_profile(db, user.id)
    return {
        "email": user.email or "",
        "phone": user.phone or "",
        "fileId": prof.file_id or "",
        "fileUri": "",
        "fileThumbnailUri": "",
        "bankAccountName": prof.bank_account_name or "",
        "bankAccountHolder": prof.bank_account_holder or "",
        "bankAccountNumber": prof.bank_account_number or "",
    }
