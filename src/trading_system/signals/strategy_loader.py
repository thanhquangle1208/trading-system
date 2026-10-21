"""Đọc chiến lược YAML trong configs/strategies/."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from trading_system.settings import REPO_ROOT
from trading_system.signals.models import ConditionSpec, StrategySpec

STRATEGIES_DIR = REPO_ROOT / "configs" / "strategies"


def _parse_condition(raw: dict[str, Any]) -> ConditionSpec:
    return ConditionSpec(
        id=str(raw["id"]),
        indicator=str(raw["indicator"]),
        signal=raw.get("signal"),
        value_key=raw.get("value_key"),
        equals=raw.get("equals", True),
        op=str(raw.get("op", "eq")),
        points=float(raw.get("points", 0)),
        compare_to=float(raw["compare_to"]) if raw.get("compare_to") is not None else None,
    )


def load_strategy(path: str | Path) -> StrategySpec:
    p = Path(path)
    if not p.is_absolute():
        p = STRATEGIES_DIR / p
    with p.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Strategy YAML phải là object: {p}")

    conf = data.get("confluence") or {}
    indicators = data.get("indicators") or []
    indicator_ids = [str(i["id"]) for i in indicators if isinstance(i, dict) and "id" in i]

    # Tự thêm indicator từ điều kiện nếu thiếu trong list
    for block in (conf.get("required") or []) + (conf.get("optional") or []):
        ind = str(block.get("indicator", ""))
        if ind and ind not in indicator_ids:
            indicator_ids.append(ind)

    return StrategySpec(
        id=str(data["id"]),
        display_name=str(data.get("display_name", data["id"])),
        enabled=bool(data.get("enabled", True)),
        symbol=str(data.get("symbol", "BTC/USDT")),
        market_type=str(data.get("market_type", "spot")),
        timeframes=list(data.get("timeframes") or ["H1"]),
        direction=str(data.get("direction", "long")).lower(),
        score_threshold=float(conf.get("score_threshold", 60)),
        score_max=float(conf.get("score_max", 100)),
        required=[_parse_condition(c) for c in (conf.get("required") or [])],
        optional=[_parse_condition(c) for c in (conf.get("optional") or [])],
        indicator_ids=indicator_ids,
        raw=data,
    )


def list_strategy_files() -> list[Path]:
    if not STRATEGIES_DIR.exists():
        return []
    return sorted(STRATEGIES_DIR.glob("*.yaml"))
