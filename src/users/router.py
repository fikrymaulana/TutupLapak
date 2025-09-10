# src/users/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.auth.dependencies import get_current_user
from src.auth.models import User
from .schemas import UpdateProfileRequest, UserProfileResponse, LinkPhoneRequest, LinkEmailRequest  
from . import service

router = APIRouter(prefix="/v1/user", tags=["profile"])

@router.get("", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "email": current_user.email or "",
        "phone": current_user.phone or "",
        "fileId": current_user.file_id or "",
        "fileUri": "",
        "fileThumbnailUri": "",
        "bankAccountName": getattr(current_user, "bank_account_name", "") or "",
        "bankAccountHolder": getattr(current_user, "bank_account_holder", "") or "",
        "bankAccountNumber": getattr(current_user, "bank_account_number", "") or "",
    }

@router.put("", response_model=UserProfileResponse)
def update_profile(
    body: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.file_id = (body.fileId or "").strip() or None
    current_user.bank_account_name = body.bankAccountName
    current_user.bank_account_holder = body.bankAccountHolder
    current_user.bank_account_number = body.bankAccountNumber

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {
        "email": current_user.email or "",
        "phone": current_user.phone or "",
        "fileId": current_user.file_id or "",
        "fileUri": "",
        "fileThumbnailUri": "",
        "bankAccountName": current_user.bank_account_name or "",
        "bankAccountHolder": current_user.bank_account_holder or "",
        "bankAccountNumber": current_user.bank_account_number or "",
    }

@router.post("/link/phone", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
def link_phone(
    payload: LinkPhoneRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_user = service.link_phone(current_user, payload.phone, db)
    return {
        "email": updated_user.email or "",
        "phone": updated_user.phone or "",
        "fileId": updated_user.file_id or "",
        "fileUri": "",
        "fileThumbnailUri": "",
        "bankAccountName": updated_user.bank_account_name or "",
        "bankAccountHolder": updated_user.bank_account_holder or "",
        "bankAccountNumber": updated_user.bank_account_number or "",
    }

@router.post("/link/email", status_code=status.HTTP_200_OK)
def link_email(
    payload: LinkEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated_user = service.link_email(current_user, payload.email, db)
    return {
        "email": updated_user.email or "",
        "phone": updated_user.phone or "",
        "fileId": updated_user.file_id or "",
        "fileUri": "",
        "fileThumbnailUri": "",
        "bankAccountName": updated_user.bank_account_name or "",
        "bankAccountHolder": updated_user.bank_account_holder or "",
        "bankAccountNumber": updated_user.bank_account_number or "",
    }