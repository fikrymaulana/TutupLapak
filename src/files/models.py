from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FileObject(Base):
    __tablename__ = "files"

    # internal primary key (explicit id). Generate with cuid2 in service before insert.
    id = Column(String(36), primary_key=True, index=True, nullable=False)

    # public file identifier (also created with cuid2)
    fileId = Column(String(36), unique=True, index=True, nullable=False)

    # URLs stored as text (public URLs)
    fileUri = Column(Text, nullable=False)
    fileThumbnailUri = Column(Text, nullable=False)
