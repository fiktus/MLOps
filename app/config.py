from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        protected_namespaces=(),###
    )
    model_path: Path = BASE_DIR/"artifacts"/"model.joblib"
    metadata_path: Path = BASE_DIR/"artifacts"/"model_metadata.json"
    database_url: str = "postgresql+psycopg://app:app@localhost:5432/app"

@lru_cache
def get_settings():
    return Settings()