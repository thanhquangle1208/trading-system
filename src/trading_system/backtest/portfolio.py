"""Mô phỏng vị thế paper trong backtest."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OpenPosition:
    side: str  # buy = long
    qty: float
    entry: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    partial_tp_pct: float
    rating: int | None
    entry_bar: int
    remaining_qty: float | None = None
    partial_done: bool = False

    def __post_init__(self) -> None:
        if self.remaining_qty is None:
            self.remaining_qty = self.qty


@dataclass
class ClosedTrade:
    side: str
    qty: float
    entry: float
    exit: float
    pnl: float
    fees: float
    rating: int | None
    exit_reason: str
    entry_bar: int
    exit_bar: int


@dataclass
class Portfolio:
    balance: float
    position: OpenPosition | None = None
    trades: list[ClosedTrade] = field(default_factory=list)
    total_fees: float = 0.0
    equity_curve: list[float] = field(default_factory=list)

    def mark_equity(self, mark_price: float | None = None) -> float:
        eq = self.balance
        if self.position and mark_price is not None:
            pos = self.position
            qty = pos.remaining_qty or 0.0
            if pos.side == "buy":
                eq += qty * (mark_price - pos.entry)
            else:
                eq += qty * (pos.entry - mark_price)
        self.equity_curve.append(eq)
        return eq
