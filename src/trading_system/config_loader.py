"""Đọc file YAML trong configs/."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from trading_system.settings import REPO_ROOT

CONFIGS_DIR = REPO_ROOT / "configs"


def load_yaml(relative_or_absolute: str | Path) -> dict[str, Any]:
    path = Path(relative_or_absolute)
    if not path.is_absolute():
        path = CONFIGS_DIR / path
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML phải là object/map: {path}")
    return data


def load_watchlist() -> dict[str, Any]:
    return load_yaml("watchlist.yaml")


def load_exchanges() -> dict[str, Any]:
    return load_yaml("exchanges.yaml")


def load_risk() -> dict[str, Any]:
    return load_yaml("risk.yaml")


def load_notify() -> dict[str, Any]:
    return load_yaml("notify.yaml")
