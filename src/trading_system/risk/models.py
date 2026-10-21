"""Kế hoạch lệnh sau khi qua risk engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OrderPlan:
    symbol: str
    side: str
    quantity: float
    entry_price: float
    stop_loss: float | None
    take_profit_1: float | None
    take_profit_2: float | None
    partial_tp_pct: float
    market_type: str
    rating: int | None
    risk_usdt: float
    atr: float | None
    approved: bool
    reject_reason: str | None = None
    hold_losers_allowed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit_1": self.take_profit_1,
            "take_profit_2": self.take_profit_2,
            "partial_tp_pct": self.partial_tp_pct,
            "market_type": self.market_type,
            "rating": self.rating,
            "risk_usdt": self.risk_usdt,
            "atr": self.atr,
            "approved": self.approved,
            "reject_reason": self.reject_reason,
            "hold_losers_allowed": self.hold_losers_allowed,
        }
