from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Finance Dashboard API")
    environment: str = Field(default="development")
    secret_key: str = Field(default="replace-me")
    access_token_expire_minutes: int = Field(default=60)
    algorithm: str = Field(default="HS256")
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/finance_db"
    )
    first_admin_name: str = Field(default="System Admin")
    first_admin_email: str = Field(default="admin@example.com")
    first_admin_password: str = Field(default="")
    auto_create_tables: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
