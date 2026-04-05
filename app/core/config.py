from functools import lru_cache
import json
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


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

    cors_allow_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["*"]
    )
    cors_allow_credentials: bool = Field(default=False)
    cors_allow_methods: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["*"]
    )
    cors_allow_headers: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["*"]
    )

    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=100, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)
    rate_limit_exempt_paths: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["/health", "/docs", "/redoc", "/openapi.json"]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator(
        "cors_allow_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        "rate_limit_exempt_paths",
        mode="before",
    )
    @classmethod
    def parse_csv_or_json_list(cls, value: Any) -> Any:
        if isinstance(value, str):
            raw_value = value.strip()
            if raw_value.startswith("[") and raw_value.endswith("]"):
                try:
                    parsed = json.loads(raw_value)
                    if isinstance(parsed, list):
                        return [str(item).strip() for item in parsed if str(item).strip()]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in raw_value.split(",") if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
