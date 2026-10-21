"""Chỉ số backtest: PnL, winrate, drawdown, phí."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from trading_system.backtest.portfolio import ClosedTrade, Portfolio


@dataclass
class BacktestMetrics:
    initial_balance: float
    final_equity: float
    net_pnl: float
    return_pct: float
    n_trades: int
    n_wins: int
    winrate: float
    total_fees: float
    max_drawdown_pct: float
    avg_rating: float | None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def max_drawdown_pct(equity_curve: list[float]) -> float:
    if not equity_curve:
        return 0.0
    peak = equity_curve[0]
    max_dd = 0.0
    for x in equity_curve:
        peak = max(peak, x)
        if peak > 0:
            dd = (peak - x) / peak * 100.0
            max_dd = max(max_dd, dd)
    return max_dd


def compute_metrics(portfolio: Portfolio, initial_balance: float) -> BacktestMetrics:
    trades = portfolio.trades
    n = len(trades)
    wins = sum(1 for t in trades if t.pnl > 0)
    final = portfolio.equity_curve[-1] if portfolio.equity_curve else portfolio.balance
    ratings = [t.rating for t in trades if t.rating is not None]
    avg_rating = sum(ratings) / len(ratings) if ratings else None
    return BacktestMetrics(
        initial_balance=initial_balance,
        final_equity=final,
        net_pnl=final - initial_balance,
        return_pct=((final - initial_balance) / initial_balance * 100.0) if initial_balance else 0.0,
        n_trades=n,
        n_wins=wins,
        winrate=(wins / n * 100.0) if n else 0.0,
        total_fees=portfolio.total_fees,
        max_drawdown_pct=max_drawdown_pct(portfolio.equity_curve),
        avg_rating=avg_rating,
    )


def summarize_trades(trades: list[ClosedTrade]) -> list[dict[str, Any]]:
    return [
        {
            "side": t.side,
            "qty": t.qty,
            "entry": t.entry,
            "exit": t.exit,
            "pnl": t.pnl,
            "fees": t.fees,
            "rating": t.rating,
            "exit_reason": t.exit_reason,
            "entry_bar": t.entry_bar,
            "exit_bar": t.exit_bar,
        }
        for t in trades
    ]
