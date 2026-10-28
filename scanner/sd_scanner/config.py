"""Đọc .env + watchlist.yaml."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
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
class AlertQuality:
    cooldown_sec: int = 1800
    side_cooldown_sec: int = 3600
    alert_timeframes: list[str] = field(default_factory=lambda: ["H4", "D1", "W1"])
    min_depth_score: float = 7.0
    min_aligned_tfs: int = 2
    min_depth_band: int = 2
    # Nấc 1: bias khung tuần — MUA chỉ khi giá > EMA W1; BÁN khi giá < EMA W1
    require_w1_ema_bias: bool = True
    w1_ema_length: int = 34


@dataclass
class Settings:
    telegram_token: str
    telegram_chat_id: str
    watch_interval_sec: int
    alert_cooldown_sec: int
    symbols: list[str]
    timeframes: list[str]
    zone: ZoneParams
    watchlist_path: Path
    quality: AlertQuality


def load_settings() -> Settings:
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

    a = raw.get("alert") or {}
    cooldown_min = float(a.get("cooldown_minutes", 30))
    side_cd_min = float(a.get("side_cooldown_minutes", 60))
    cooldown_env = os.getenv("ALERT_COOLDOWN_SEC")
    cooldown_sec = int(cooldown_env) if cooldown_env else int(cooldown_min * 60)

    alert_tfs = [str(t).upper() for t in (a.get("alert_timeframes") or ["H4", "D1", "W1"])]
    quality = AlertQuality(
        cooldown_sec=max(60, cooldown_sec),
        side_cooldown_sec=max(60, int(side_cd_min * 60)),
        alert_timeframes=alert_tfs,
        min_depth_score=float(a.get("min_depth_score", 7.0)),
        min_aligned_tfs=int(a.get("min_aligned_tfs", 2)),
        min_depth_band=int(a.get("min_depth_band", 2)),
        require_w1_ema_bias=bool(a.get("require_w1_ema_bias", True)),
        w1_ema_length=max(2, int(a.get("w1_ema_length", 34))),
    )

    symbols = [str(s).upper().replace(".P", "").replace("/", "") for s in (raw.get("symbols") or [])]
    timeframes = [str(t).upper() for t in (raw.get("timeframes") or ["H1", "H4", "D1", "W1"])]
    if not symbols:
        raise SystemExit("watchlist.yaml: danh sách symbols trống.")

    return Settings(
        telegram_token=token,
        telegram_chat_id=chat_id,
        watch_interval_sec=max(15, interval),
        alert_cooldown_sec=quality.cooldown_sec,
        symbols=symbols,
        timeframes=timeframes,
        zone=zone,
        watchlist_path=wl_path,
        quality=quality,
    )
