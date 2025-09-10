# src/auth/models.py
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from cuid2 import cuid_wrapper

generate_cuid = cuid_wrapper()

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        default=generate_cuid,
    )

    # email boleh kosong kalau daftar via phone
    email: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )

    phone: Mapped[Optional[str]] = mapped_column(
        String(50), unique=True, index=True, nullable=True
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Placeholder untuk file_id (nanti dihubungkan ke tabel files)
    file_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True
    )

    # ✅ Tambahkan kolom bank account di dalam class
    bank_account_name: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    bank_account_holder: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    bank_account_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
