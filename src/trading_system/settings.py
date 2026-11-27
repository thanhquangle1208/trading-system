"""Đọc cấu hình từ biến môi trường (.env) — không hard-code secret."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    log_level: str = "INFO"
    timezone: str = "Asia/Ho_Chi_Minh"

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    notion_token: str = ""
    notion_database_id: str = "41e859693b1581cc80bbfbcd6fe9e8c3"
    notion_data_source_id: str = "41e85969-3b15-815a-9e5e-000b774bd208"

    coingecko_api_key: str = ""

    @field_validator("notion_database_id", "notion_data_source_id", mode="before")
    @classmethod
    def blank_ids_keep_default(cls, value: object, info) -> object:
        """Secret trống trên GitHub Actions không được xóa id mặc định."""
        if not isinstance(value, str) or not value.strip():
            return cls.model_fields[info.field_name].default
        return value.strip()


@lru_cache
def get_settings() -> Settings:
    return Settings()
