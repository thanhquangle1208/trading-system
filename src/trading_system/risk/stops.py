"""SL / TP (partial + runner) từ entry + ATR."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StopLevels:
    stop_loss: float
    take_profit_1: float
    take_profit_2: float


def compute_stop_levels(
    *,
    entry: float,
    side: str,
    atr: float,
    atr_stop_mult: float,
    atr_tp1_mult: float,
    atr_tp2_mult: float,
) -> StopLevels:
    if entry <= 0 or atr <= 0:
        raise ValueError("entry và atr phải > 0")
    side_n = side.lower()
    sl_dist = atr * atr_stop_mult
    tp1_dist = atr * atr_tp1_mult
    tp2_dist = atr * atr_tp2_mult

    if side_n in ("buy", "long"):
        return StopLevels(
            stop_loss=entry - sl_dist,
            take_profit_1=entry + tp1_dist,
            take_profit_2=entry + tp2_dist,
        )
    if side_n in ("sell", "short"):
        return StopLevels(
            stop_loss=entry + sl_dist,
            take_profit_1=entry - tp1_dist,
            take_profit_2=entry - tp2_dist,
        )
    raise ValueError(f"side không hợp lệ: {side}")
