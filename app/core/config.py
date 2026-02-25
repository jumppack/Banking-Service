from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "Banking Service"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/banking.db"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "dev"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.SECRET_KEY in {"changeme", "change_me", "supersecretkey"}:
            raise ValueError("SECRET_KEY must be a strong, unique value in production.")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
