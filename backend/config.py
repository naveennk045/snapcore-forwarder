from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):

    # Database
    DB_URL: str = Field(..., description="PostgreSQL connection URL")

    # Pydantic v2 modern config
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8"
    )

#  Singleton cached settings
@lru_cache()
def get_settings() -> Settings:
    return Settings()
