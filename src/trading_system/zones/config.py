"""Đọc configs/buy_zones.yaml và vài biến môi trường ghi đè."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from trading_system.settings import REPO_ROOT


@dataclass(frozen=True)
class BuyZoneConfig:
    hysteresis_pct: float = 2.0
    approaching_pct: float | None = None
    digest_enabled: bool = True
    digest_hour_vn: int = 7
    digest_minute_vn: int = 5
    state_path: str = ".state/buy_zones.json"
    timezone: str = "Asia/Ho_Chi_Minh"
    lease_max_age_sec: int = 20 * 60

    @property
    def hysteresis(self) -> float:
        """Tỷ lệ, ví dụ 2% → 0.02."""
        return max(0.0, self.hysteresis_pct) / 100.0

    @property
    def approaching(self) -> float | None:
        if self.approaching_pct is None or self.approaching_pct <= 0:
            return None
        return self.approaching_pct / 100.0


def _optional_float(value: object) -> float | None:
    if value is None or value == "":
        return None
    return float(value)  # type: ignore[arg-type]


def load_buy_zone_config(
    path: Path | None = None,
    *,
    timezone: str = "Asia/Ho_Chi_Minh",
) -> BuyZoneConfig:
    path = path or (REPO_ROOT / "configs" / "buy_zones.yaml")
    raw: dict = {}
    if path.exists():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(loaded, dict):
            raw = loaded
    digest = raw.get("digest") or {}
    state = raw.get("state") or {}
    lease = raw.get("lease") or {}

    hysteresis = float(raw.get("hysteresis_pct", 2.0))
    approaching = _optional_float(raw.get("approaching_pct"))

    env_h = os.getenv("BUY_ZONE_HYSTERESIS_PCT")
    if env_h:
        hysteresis = float(env_h)
    env_a = os.getenv("BUY_ZONE_APPROACHING_PCT")
    if env_a is not None and env_a.strip() != "":
        if env_a.strip().lower() in {"off", "none", "null"}:
            approaching = None
        else:
            approaching = float(env_a)

    state_path = os.getenv("BUY_ZONE_STATE_PATH") or state.get("path") or ".state/buy_zones.json"
    lease_minutes = int(lease.get("max_age_minutes", 20))
    return BuyZoneConfig(
        hysteresis_pct=hysteresis,
        approaching_pct=approaching,
        digest_enabled=bool(digest.get("enabled", True)),
        digest_hour_vn=int(digest.get("hour_vn", 7)),
        digest_minute_vn=int(digest.get("minute_vn", 5)),
        state_path=str(state_path),
        timezone=timezone,
        lease_max_age_sec=max(60, lease_minutes * 60),
    )
