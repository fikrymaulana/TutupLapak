#src/auth/config.py
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Variabel ini akan dibaca dari .env
    DATABASE_URL: str
    SECRET_KEY: str

    # Variabel ini bisa kita beri nilai default di sini
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Buat satu instance 'settings' yang akan kita import di file lain
settings = Settings()