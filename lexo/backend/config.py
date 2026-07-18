from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Required from env — empty default only so the Neon-specific validator message always fires.
    database_url: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]
    # Required from env — empty default only so the JWT-specific validator message always fires.
    jwt_secret: str = ""
    gemini_api_key: str = ""
    exa_api_key: str = ""
    elevenlabs_api_key: str = ""
    wispr_api_key: str = ""
    upload_dir: str = "./uploads"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if not v or not str(v).strip():
            raise ValueError(
                "DATABASE_URL is required. Paste your Neon pooled connection string "
                "from the neon.tech console into lexo/backend/.env "
                "(postgresql://...?sslmode=require)."
            )
        url = str(v).strip()
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://") :]
        if not url.startswith("postgresql://"):
            raise ValueError(
                "DATABASE_URL must be a Neon Postgres connection string "
                "(postgresql://... or postgres://...), not SQLite or another driver."
            )
        return url

    @field_validator("jwt_secret")
    @classmethod
    def require_jwt_secret(cls, v: str) -> str:
        secret = (v or "").strip()
        if not secret:
            raise ValueError(
                "JWT_SECRET is required and must be non-empty. "
                "Set a long random string in lexo/backend/.env "
                "(e.g. openssl rand -hex 32)."
            )
        return secret


settings = Settings()
