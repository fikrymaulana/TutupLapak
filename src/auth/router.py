from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import re

from src.database import get_db
from . import schemas, service

# Prefix hanya domain, tanpa versi
router = APIRouter(prefix="/v1", tags=["Authentication"])


@router.post("/register/email", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def register_by_email(payload: dict = Body(..., example={"email": "user@example.com", "password": "Secret123"}), db: Session = Depends(get_db)):
    # --- VALIDASI MANUAL (agar 400, bukan 422) ---
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Bad Request")

    email = payload.get("email", None)
    password = payload.get("password", None)

    # body kosong / field hilang
    if email is None or password is None:
        raise HTTPException(status_code=400, detail="Bad Request")

    # tipe harus string
    if not isinstance(email, str) or not isinstance(password, str):
        raise HTTPException(status_code=400, detail="Bad Request")

    # email minimal ada '@' (sesuai yang dicek di load test)
    if "@" not in email or email.count("@") != 1 or email.startswith("@") or email.endswith("@"):
        raise HTTPException(status_code=400, detail="Bad Request")

    # panjang password 8..32
    if len(password) < 8 or len(password) > 32:
        raise HTTPException(status_code=400, detail="Bad Request")

    # --- CEK KONFLIK EMAIL (409) ---
    if service.get_user_by_email(db, email=email):
        raise HTTPException(status_code=409, detail="Email is exist")

    # --- CREATE USER ---
    try:
        new_user = service.create_user(db=db, user_data=schemas.UserCreate(email=email, password=password))
    except IntegrityError:
        # jaga-jaga kalau unique constraint yg nembak langsung dari DB
        raise HTTPException(status_code=409, detail="Email is exist")
    except Exception:
        # supaya nggak meledak 500 tanpa kontrol; load test memang expect "Internal Server Error" saat 500
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # --- CREATE TOKEN ---
    try:
        token = service.create_access_token(data={"sub": str(new_user.id)}, user=new_user)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    return {"email": new_user.email or "", "phone": new_user.phone or "", "token": token}

@router.post("/register/phone", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
def register_by_phone(user_data: schemas.UserCreatePhone, db: Session = Depends(get_db)):
    if service.get_user_by_phone(db, phone=user_data.phone):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="phone is exist")

    try:
        new_user = service.create_user(db=db, user_data=user_data)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="phone is exist")

    token = service.create_access_token(data={"sub": str(new_user.id)}, user=new_user)
    return {"email": new_user.email or "", "phone": new_user.phone or "", "token": token}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")  # simple enough for test

def _bad_request():
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad Request")

def _parse_json_or_400(body):
    if not isinstance(body, dict):
        _bad_request()
    return body

def _validate_login_email_payload_or_400(body):
    # wajib ada key
    if "email" not in body or "password" not in body:
        _bad_request()

    email = body["email"]
    password = body["password"]

    # tipe harus string
    if not isinstance(email, str) or not isinstance(password, str):
        _bad_request()

    email = email.strip()

    # email format minimal (sesuai test-k6: string tanpa '@' dianggap bad request)
    if not email or "@" not in email:
        _bad_request()
    # boleh dipertegas, tapi regex simple aja cukup utk test
    if not EMAIL_RE.match(email):
        _bad_request()

    # password length 8..32, empty string juga 400
    if not (8 <= len(password) <= 32):
        _bad_request()

    return email, password

# --- REGISTER tetap seperti punyamu sekarang (sudah lolos test) ---------
# ... (biarkan kode register kamu yang sudah jalan)

# --- LOGIN (email) dengan IF murni --------------------------------------

@router.post("/login/email", response_model=schemas.TokenResponse)
async def login_by_email(request: Request, db: Session = Depends(get_db)):
    # baca json mentah
    try:
        body = await request.json()
    except Exception:
        _bad_request()

    body = _parse_json_or_400(body)
    email, password = _validate_login_email_payload_or_400(body)

    # email tidak terdaftar -> 404 (sesuai skenario k6)
    db_user = service.get_user_by_email(db, email=email)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

    # salah password -> 401 (keep behaviour)
    # gunakan authenticate_user milikmu agar hashing/verify tetap konsisten
    user = service.authenticate_user(db, user_data=schemas.UserLogin(email=email, password=password))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = service.create_access_token(data={"sub": str(user.id)}, user=user)
    return {"email": user.email or "", "phone": user.phone or "", "token": token}

# --- OPTIONAL: LOGIN (phone) kalau mau diseragamkan 400 utk payload jelek ----
@router.post("/login/phone", response_model=schemas.TokenResponse)
async def login_by_phone(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
    except Exception:
        _bad_request()
    body = _parse_json_or_400(body)

    if "phone" not in body or "password" not in body:
        _bad_request()
    phone = body["phone"]
    password = body["password"]
    if not isinstance(phone, str) or not isinstance(password, str):
        _bad_request()
    # E.164 simple check
    if not re.match(r"^\+[1-9]\d{1,14}$", phone or ""):
        _bad_request()
    if not (8 <= len(password) <= 32):
        _bad_request()

    user = service.authenticate_user_by_phone(db, phone=phone, password=password)
    if not user:
        # kamu sebelumnya pakai 404 untuk phone; boleh dipertahankan jika test butuh
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="phone is not found or password incorrect",
        )

    token = service.create_access_token(data={"sub": str(user.id)}, user=user)
    return {"email": user.email or "", "phone": user.phone or "", "token": token}
