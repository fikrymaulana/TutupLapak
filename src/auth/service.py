from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta, timezone
import jwt

from . import models, schemas
from .utils import hash_password, verify_password
from .config import settings

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_phone(db: Session, phone: str):
    return db.query(models.User).filter(models.User.phone == phone).first()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def create_user(db: Session, user_data: schemas.UserCreate | schemas.UserCreatePhone):
    hashed_password = hash_password(user_data.password)
    user_dict = user_data.model_dump()
    user_dict.pop("password")

    db_user = models.User(**user_dict, password_hash=hashed_password)
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(db_user)
    return db_user

# Opsi A: Login via email saja (seperti punyamu)
def authenticate_user(db: Session, user_data: schemas.UserLogin):
    user = get_user_by_email(db, email=user_data.email)
    if not user:
        return None
    if not verify_password(user_data.password, user.password_hash):
        return None
    return user

def authenticate_user_by_phone(db: Session, phone: str, password: str):
    user = get_user_by_phone(db, phone=phone)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

# Opsi B (alternatif): jika mau dukung phone
# def authenticate_user(db: Session, email: str | None = None, phone: str | None = None, password: str = ""):
#     user = get_user_by_email(db, email) if email else get_user_by_phone(db, phone) if phone else None
#     if not user or not verify_password(password, user.password_hash):
#         return None
#     return user
