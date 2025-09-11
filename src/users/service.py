from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.auth import models as auth_models
from src.users import models as user_models

def get_or_create_profile(db: Session, user_id: str) -> user_models.Profile:
    prof = db.query(user_models.Profile).filter(user_models.Profile.user_id == user_id).first()
    if prof:
        return prof
    prof = user_models.Profile(user_id=user_id)
    db.add(prof)
    db.commit()
    db.refresh(prof)
    return prof

def update_profile(db: Session, user: auth_models.User, *, file_id: str | None,
                   bank_name: str | None, bank_holder: str | None, bank_number: str | None) -> user_models.Profile:
    prof = get_or_create_profile(db, user.id)
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
