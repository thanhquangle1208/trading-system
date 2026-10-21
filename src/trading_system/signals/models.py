"""Kiểu dữ liệu chiến lược & tín hiệu (Phase 3)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConditionSpec:
    """Một điều kiện đọc từ YAML."""

    id: str
    indicator: str
    signal: str | None = None
    value_key: str | None = None
    equals: Any = True
    op: str = "eq"  # eq | gt | gte | lt | lte
    points: float = 0.0
    compare_to: float | None = None  # dùng với value_key + op số


@dataclass
class StrategySpec:
    id: str
    display_name: str
    enabled: bool
    symbol: str
    market_type: str
    timeframes: list[str]
    direction: str  # long | short
    score_threshold: float
    score_max: float
    required: list[ConditionSpec]
    optional: list[ConditionSpec]
    indicator_ids: list[str]
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ConditionEval:
    condition_id: str
    passed: bool
    points_awarded: float
    detail: str


@dataclass
class SignalResult:
    """Một tín hiệu (hoặc không có tín hiệu) sau confluence."""

    strategy_id: str
    display_name: str
    symbol: str
    timeframe: str
    direction: str | None
    fired: bool
    score: float
    score_threshold: float
    rating: int | None  # Độ tin cậy 1–10 khi fired
    required_ok: bool
    evaluations: list[ConditionEval]
    indicator_snapshot: dict[str, Any] = field(default_factory=dict)
    reason: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "display_name": self.display_name,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "direction": self.direction,
            "fired": self.fired,
            "score": self.score,
            "score_threshold": self.score_threshold,
            "rating": self.rating,
            "required_ok": self.required_ok,
            "reason": self.reason,
            "evaluations": [
                {
                    "id": e.condition_id,
                    "passed": e.passed,
                    "points": e.points_awarded,
                    "detail": e.detail,
                }
                for e in self.evaluations
            ],
        }
