"""Interface chung cho mọi chỉ báo / module (plugin)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Sequence

from trading_system.data.base import Candle


@dataclass
class IndicatorResult:
    """Kết quả một lần compute — số liệu + cờ/tín hiệu đơn giản."""

    indicator_id: str
    display_name: str
    values: dict[str, Any] = field(default_factory=dict)
    series: dict[str, list[float | None]] = field(default_factory=dict)
    signals: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "indicator_id": self.indicator_id,
            "display_name": self.display_name,
            "values": self.values,
            "series": self.series,
            "signals": self.signals,
        }


class IndicatorPlugin(ABC):
    """Mỗi chỉ báo một class, cùng cách gọi compute(candles)."""

    id: str
    display_name: str

    @abstractmethod
    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        """Tính trên chuỗi nến. Không phụ thuộc sàn."""


def require_min_candles(candles: Sequence[Candle], n: int, name: str) -> None:
    if len(candles) < n:
        raise ValueError(f"{name} cần ít nhất {n} nến, đang có {len(candles)}")
