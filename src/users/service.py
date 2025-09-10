# src/users/service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.auth import models


def link_phone(user: models.User, phone: str, db: Session) -> models.User:
    """
    Link (or relink) a phone number to the current user.
    Idempotent if the phone is already the user's phone.
    """
    phone = (phone or "").strip()

    existing = (
        db.query(models.User)
        .filter(models.User.phone == phone)
        .first()
    )
    # If someone else already owns this phone -> conflict
    if existing and existing.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="phone is taken",
        )

    # If this user already has the same phone, it's fine (no-op)
    if user.phone == phone:
        return user

    user.phone = phone
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def link_email(user: models.User, email: str, db: Session) -> models.User:
    """
    Link (or relink) an email to the current user.
    Idempotent if the email is already the user's email.
    """
    email = (email or "").strip().lower()  # normalize (optional)

    existing = (
        db.query(models.User)
        .filter(models.User.email == email)
        .first()
    )
    # If someone else already owns this email -> conflict
    if existing and existing.id != user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email is taken",
        )

    # No-op if unchanged
    if user.email == email:
        return user

    user.email = email
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
