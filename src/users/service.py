
# src/users/service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from src.auth import models as auth_models
from src.users import models as user_models
from src.users.schemas import UserProfileResponse
from src.files.models import FileObject  # asumsi punya kolom: id, fileId, fileUri, fileThumbnailUri


# ---------- helpers ----------
def _s(v: str | None) -> str:
    return v or ""


def _find_fileobj(db: Session, any_id: str | None) -> FileObject | None:
    """
    Cari file berdasarkan 'public id' (fileId) dulu.
    Kalau tidak ketemu, fallback cari berdasarkan 'internal id' (id).
    """
    if not any_id:
        return None

    # 1) coba cocokan ke kolom fileId (public id)
    f = db.query(FileObject).filter(getattr(FileObject, "fileId") == any_id).first()
    if f:
        return f

    # 2) fallback: cocokkan ke kolom id (internal id)
    return db.query(FileObject).filter(FileObject.id == any_id).first()


def _to_response(user: auth_models.User, prof: user_models.Profile | None, db: Session) -> UserProfileResponse:
    file_uri = ""
    file_thumb = ""

    if prof and prof.file_id:
        f = _find_fileobj(db, prof.file_id)
        if f:
            # atribut sesuai model FileObject kamu (camelCase)
            file_uri = _s(getattr(f, "fileUri", None))
            file_thumb = _s(getattr(f, "fileThumbnailUri", None))

    return UserProfileResponse(
        email=_s(user.email),
        phone=_s(user.phone),
        fileId=_s(prof.file_id) if prof else "",
        fileUri=file_uri,
        fileThumbnailUri=file_thumb,
        bankAccountName=_s(prof.bank_account_name) if prof else "",
        bankAccountHolder=_s(prof.bank_account_holder) if prof else "",
        bankAccountNumber=_s(prof.bank_account_number) if prof else "",
    )


# ---------- core services ----------

def get_or_create_profile(db: Session, user_id: str) -> user_models.Profile:
    prof = db.query(user_models.Profile).filter(user_models.Profile.user_id == user_id).first()
    if prof:
        return prof
    prof = user_models.Profile(user_id=user_id)
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof


def get_profile(db: Session, user: auth_models.User) -> UserProfileResponse:
    prof = db.query(user_models.Profile).filter(user_models.Profile.user_id == user.id).first()
    return _to_response(user, prof, db)


def update_profile(
    db: Session,
    user: auth_models.User,
    *,
    file_id: str | None,
    bank_name: str | None,
    bank_holder: str | None,
    bank_number: str | None,
) -> user_models.Profile:
    prof = get_or_create_profile(db, user.id)

    # normalize

    prof.file_id = (file_id or "").strip() or None
    prof.bank_account_name = bank_name or ""
    prof.bank_account_holder = bank_holder or ""
    prof.bank_account_number = bank_number or ""



    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof




def link_phone(user: auth_models.User, phone: str, db: Session):
    existing = db.query(auth_models.User).filter(auth_models.User.phone == phone).first()
    if existing and existing.id != user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="phone is taken")
    user.phone = phone
    db.add(user)
    db.commit()
    db.refresh(user)
    return user



def link_email(user: auth_models.User, email: str, db: Session):
    existing = db.query(auth_models.User).filter(auth_models.User.email == email).first()
    if existing and existing.id != user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email is taken")
    user.email = email
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def set_profile_file_id(
    db: Session,
    user: auth_models.User,
    file_internal_id: Optional[str],
    *,
    overwrite: bool = True,
) -> user_models.Profile:
    prof = db.query(user_models.Profile).filter_by(user_id=user.id).first()
    if not prof:
        prof = user_models.Profile(user_id=user.id)
        db.add(prof)
        db.flush()  # biar prof.id terisi dalam transaksi yang sama

    if overwrite or not prof.file_id:
        prof.file_id = file_internal_id

    db.add(prof)
    return prof

