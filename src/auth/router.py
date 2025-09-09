from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database import get_db
from . import schemas, service

# Prefix hanya domain, tanpa versi
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register/email", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def register_by_email(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    if service.get_user_by_email(db, email=user_data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is exist")

    try:
        new_user = service.create_user(db=db, user_data=user_data)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is exist")

    token = service.create_access_token(data={"sub": str(new_user.id)})
    return {"email": new_user.email or "", "phone": new_user.phone or "", "token": token}

@router.post("/register/phone", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def register_by_phone(user_data: schemas.UserCreatePhone, db: Session = Depends(get_db)):
    if service.get_user_by_phone(db, phone=user_data.phone):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="phone is exist")

    try:
        new_user = service.create_user(db=db, user_data=user_data)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="phone is exist")

    token = service.create_access_token(data={"sub": str(new_user.id)})
    return {"email": new_user.email or "", "phone": new_user.phone or "", "token": token}

@router.post("/login/email", response_model=schemas.TokenResponse)
def login_by_email(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = service.authenticate_user(db, user_data=user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = service.create_access_token(data={"sub": str(user.id)})
    return {"email": user.email or "", "phone": user.phone or "", "token": token}

@router.post("/login/phone", response_model=schemas.TokenResponse)
def login_by_phone(user_data: schemas.UserLoginPhone, db: Session = Depends(get_db)):
    user = service.authenticate_user_by_phone(db, phone=user_data.phone, password=user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="phone is not found or password incorrect",
        )
    token = service.create_access_token(data={"sub": str(user.id)})
    return {"email": user.email or "", "phone": user.phone or "", "token": token}

    