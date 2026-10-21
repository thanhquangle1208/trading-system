"""Đọc cấu hình từ biến môi trường (.env) — không hard-code secret."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
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
    database_path: str = "data/trading.db"

    paper_starting_balance_usdt: float = Field(default=1000.0, ge=0)

    exchange_id: str = "bybit"
    exchange_testnet: bool = True
    mock_exchange: bool = True
    bybit_api_key: str = ""
    bybit_api_secret: str = ""

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    def database_file(self) -> Path:
        path = Path(self.database_path)
        if not path.is_absolute():
            path = REPO_ROOT / path
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
