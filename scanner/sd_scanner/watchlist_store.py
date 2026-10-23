"""Đọc/ghi symbols trong watchlist.yaml (giữ các key khác)."""

from __future__ import annotations

from pathlib import Path

import yaml


def load_raw(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_symbols(path: Path, symbols: list[str]) -> None:
    raw = load_raw(path)
    raw["symbols"] = symbols
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(raw, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
