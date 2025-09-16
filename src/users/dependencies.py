# src/users/dependencies.py
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.database import get_db
from src.auth.models import User
from src.auth.config import settings
from . import service
import jwt, re

security = HTTPBearer(auto_error=False)

def require_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    raw_auth = request.headers.get("authorization") or request.headers.get("Authorization")
    token = None

    # 1) Format standar: Bearer <token>
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials

    # 2) Workaround: kalau tidak ada skema tapi ada header, anggap seluruhnya token
    if not token and raw_auth and " " not in raw_auth.strip():
        token = raw_auth.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Invalid token audience")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=401, detail="Invalid token issuer")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

CurrentUser = Annotated[User, Depends(require_user)]

# -------- payload validators --------
E164_RE = re.compile(r"^\+[1-9]\d{1,14}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _bad_request():
    raise HTTPException(status_code=400, detail="Bad Request")

async def validate_phone_payload(request: Request) -> str:
    try:
        body = await request.json()
    except Exception:
        _bad_request()
    if not isinstance(body, dict) or "phone" not in body:
        _bad_request()
    phone = body["phone"]
    if not isinstance(phone, str):
        _bad_request()
    phone = phone.strip()
    if not E164_RE.match(phone):
        _bad_request()
    return phone

async def require_new_phone(
    current_user: CurrentUser,
    phone: str = Depends(validate_phone_payload),
    db: Session = Depends(get_db),
    
) -> str:
    existing = service.get_user_by_phone(db, phone)
    if existing and existing.id != current_user.id:
        raise HTTPException(status_code=409, detail="phone is exist")
    return phone

async def validate_email_payload(request: Request) -> str:
    try:
        body = await request.json()
    except Exception:
        _bad_request()
    if not isinstance(body, dict) or "email" not in body:
        _bad_request()
    email = body["email"]
    if not isinstance(email, str):
        _bad_request()
    email = email.strip()
    if not EMAIL_RE.match(email):
        _bad_request()
    return email

async def require_new_email(
    current_user: CurrentUser,
    email: str = Depends(validate_email_payload),
    db: Session = Depends(get_db),
    
) -> str:
    existing = service.get_user_by_email(db, email)
    if existing and existing.id != current_user.id:
        raise HTTPException(status_code=409, detail="email is exist")
    return email