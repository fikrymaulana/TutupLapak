import secrets
from pydantic import Field
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "TutupLapak"
    debug: bool = False
    secret_key: str = Field(default_factory=lambda: secrets.token_hex(32))
    database_url: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"

settings = Settings()