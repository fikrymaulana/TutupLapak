from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from cuid2 import cuid_wrapper
from src.database import Base

generate_cuid = cuid_wrapper()

class File(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String(255), primary_key=True, default=generate_cuid)
    uri: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_uri: Mapped[str] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
