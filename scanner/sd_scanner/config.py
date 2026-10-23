"""Đọc .env + watchlist.yaml."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
SCANNER_DIR = Path(__file__).resolve().parents[1]


@dataclass
class ZoneParams:
    pivot_len: int = 5
    dep_atr: float = 1.0
    atr_len: int = 10
    max_zones: int = 8
    lookback_bars: int = 300


@dataclass
class Settings:
    telegram_token: str
    telegram_chat_id: str
    watch_interval_sec: int
    symbols: list[str]
    timeframes: list[str]
    zone: ZoneParams
    watchlist_path: Path


def load_settings() -> Settings:
    # Ưu tiên .env ở root repo, rồi scanner/
    load_dotenv(ROOT / ".env")
    load_dotenv(SCANNER_DIR / ".env")

    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    chat_id = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat_id:
        raise SystemExit(
            "Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID.\n"
            "Tạo file .env từ .env.example (ở thư mục gốc repo) rồi điền đủ."
        )

    interval = int(os.getenv("WATCH_INTERVAL_SEC") or "45")
    wl_path = SCANNER_DIR / "watchlist.yaml"
    with wl_path.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    z = raw.get("zone") or {}
    zone = ZoneParams(
        pivot_len=int(z.get("pivot_len", 5)),
        dep_atr=float(z.get("dep_atr", 1.0)),
        atr_len=int(z.get("atr_len", 10)),
        max_zones=int(z.get("max_zones", 8)),
        lookback_bars=int(z.get("lookback_bars", 300)),
    )
    symbols = [str(s).upper().replace(".P", "").replace("/", "") for s in (raw.get("symbols") or [])]
    timeframes = [str(t).upper() for t in (raw.get("timeframes") or ["H1", "H4", "D1", "W1"])]
    if not symbols:
        raise SystemExit("watchlist.yaml: danh sách symbols trống.")

    return Settings(
        telegram_token=token,
        telegram_chat_id=chat_id,
        watch_interval_sec=max(15, interval),
        symbols=symbols,
        timeframes=timeframes,
        zone=zone,
        watchlist_path=wl_path,
    )
