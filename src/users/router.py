import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.files.models import FileObject
from .schemas import UpdateProfileRequest, UserProfileResponse, LinkPhoneRequest, LinkEmailRequest
from . import service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["profile"])

@router.get("/user", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    prof = service.get_or_create_profile(db, current_user.id)
    return {
        "email": current_user.email or "",
        "phone": current_user.phone or "",
        "fileId": prof.file_id or "",
        "fileUri": "",
        "fileThumbnailUri": "",
        "bankAccountName": prof.bank_account_name or "",
        "bankAccountHolder": prof.bank_account_holder or "",
        "bankAccountNumber": prof.bank_account_number or "",
    }

@router.put("/user", response_model=UserProfileResponse)
def update_profile(
    body: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prof = service.update_profile(
        db, current_user,
        file_id=body.fileId,
        bank_name=body.bankAccountName,
        bank_holder=body.bankAccountHolder,
        bank_number=body.bankAccountNumber,
    )
    logger.info(f"Updated profile for user {current_user.id}, file_id: {prof.file_id}")

    file_uri = ""
    file_thumbnail_uri = ""
    if prof.file_id:
        file_obj = db.query(FileObject).filter(FileObject.fileId == prof.file_id).first()
        if file_obj:
            file_uri = file_obj.fileUri
            file_thumbnail_uri = file_obj.fileThumbnailUri
            logger.info(f"Found file for fileId {prof.file_id}: uri={file_uri}, thumb={file_thumbnail_uri}")
        else:
            logger.warning(f"No file found for fileId {prof.file_id}")

    return {
        "email": current_user.email or "",
        "phone": current_user.phone or "",
        "fileId": prof.file_id or "",
        "fileUri": file_uri,
        "fileThumbnailUri": file_thumbnail_uri,
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
