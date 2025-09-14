#src/auth/config.py
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Variabel ini akan dibaca dari .env
    DATABASE_URL: str
    SECRET_KEY: str

    # JWT Configuration for cross-service compatibility
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ISSUER: str = "tutuplapak-api"
    JWT_AUDIENCE: str = "tutuplapak-services"
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Buat satu instance 'settings' yang akan kita import di file lain
settings = Settings()