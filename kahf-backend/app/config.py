from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    port: int = 8000
    cors_allowed_origins: str = "http://localhost:3000"

    facecheck_api_token: str = ""
    facecheck_testing_mode: bool = True
    pimeyes_api_key: str = ""

    deepface_model: str = "Facenet512"
    confidence_threshold: float = 85.0

    session_ttl_minutes: int = 30
    session_encryption_key: str = ""

    supabase_url: str = ""
    supabase_service_key: str = ""

    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_region: str = "us-east-1"

    scraper_timeout_ms: int = 15000
    scraper_enabled: bool = True

    min_reference_photos: int = 3
    max_reference_photos: int = 5

    @property
    def cors_origins(self) -> List[str]:
        if self.cors_allowed_origins.strip() == "*":
            return ["*"]
        return [o.strip().rstrip("/") for o in self.cors_allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
