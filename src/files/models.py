from __future__ import annotations
from datetime import datetime

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from cuid2 import cuid_wrapper

Base = declarative_base()


class FileObject(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        index=True,
        nullable=False,
        default=lambda: cuid_wrapper(),
    )

    fileId: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        index=True,
        nullable=False,
        default=lambda: cuid_wrapper(),
    )

    fileUri: Mapped[str] = mapped_column(Text, nullable=False)
    fileThumbnailUri: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
