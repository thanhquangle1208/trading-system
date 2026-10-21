"""Routing multi-channel theo YAML (Phase 6 — bắt đầu 1 kênh)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from trading_system.config_loader import load_notify


@dataclass
class Channel:
    id: str
    display_name: str
    chat_id: str
    enabled: bool


@dataclass
class NotifyConfig:
    enabled: bool
    channels: dict[str, Channel]
    routes: list[dict[str, Any]]
    rating_label: str
    include_rating_bar: bool


def load_notify_config() -> NotifyConfig:
    raw = load_notify()
    template = raw.get("template") or {}
    channels: dict[str, Channel] = {}
    for ch in raw.get("channels") or []:
        env_key = ch.get("chat_id_env", "TELEGRAM_CHAT_ID")
        chat_id = os.environ.get(env_key, "") or ""
        # fallback settings via env already loaded; also allow empty for dry-run
        channels[str(ch["id"])] = Channel(
            id=str(ch["id"]),
            display_name=str(ch.get("display_name", ch["id"])),
            chat_id=chat_id,
            enabled=bool(ch.get("enabled", True)),
        )
    return NotifyConfig(
        enabled=bool(raw.get("enabled", True)),
        channels=channels,
        routes=list(raw.get("routes") or []),
        rating_label=str(template.get("rating_label", "Độ tin cậy")),
        include_rating_bar=bool(template.get("include_rating_bar", True)),
    )


def resolve_channel(
    cfg: NotifyConfig,
    *,
    timeframe: str | None = None,
    strategy_id: str | None = None,
) -> Channel | None:
    """Chọn channel theo route; không khớp → channel đầu tiên enabled."""
    for route in cfg.routes:
        match = route.get("match") or {}
        if timeframe and match.get("timeframe") and match["timeframe"] != timeframe:
            continue
        if strategy_id and match.get("strategy_id") and match["strategy_id"] != strategy_id:
            continue
        ch = cfg.channels.get(str(route.get("channel_id", "")))
        if ch and ch.enabled:
            return ch
    for ch in cfg.channels.values():
        if ch.enabled:
            return ch
    return None
