from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from minio import Minio

from .constants import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Create engine & sessionmaker (sync SQLAlchemy)
def get_engine():
    s = get_settings()
    engine = create_engine(s.DATABASE_URL, pool_pre_ping=True, future=True)
    return engine


Engine = get_engine()
SessionLocal = sessionmaker(bind=Engine, autoflush=False, autocommit=False, future=True)


# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_minio_client() -> Minio:
    s = get_settings()
    return Minio(
        endpoint=s.MINIO_ENDPOINT,
        access_key=s.MINIO_ACCESS_KEY,
        secret_key=s.MINIO_SECRET_KEY,
        secure=s.MINIO_SECURE,
    )
