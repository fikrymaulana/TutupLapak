# src/users/models.py
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from cuid2 import cuid_wrapper

cuid = cuid_wrapper()

class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=cuid)

    # One-to-one dengan users: satu user satu profile
    user_id: Mapped[str] = mapped_column(
        String(255),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        unique=True,          # enforce 1-1
    )

    # kolom profil
    file_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    bank_account_name: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    bank_account_holder: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    __table_args__ = (UniqueConstraint("user_id", name="uq_profiles_user_id"),)
