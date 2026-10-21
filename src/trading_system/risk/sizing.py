"""Tính khối lượng lệnh theo % rủi ro và ATR."""

from __future__ import annotations


def position_size_from_atr(
    *,
    balance: float,
    risk_per_trade_pct: float,
    atr: float,
    atr_stop_mult: float,
) -> tuple[float, float, float]:
    """
    Returns: (quantity_base, risk_usdt, stop_distance)
    quantity ≈ risk_usdt / stop_distance
    """
    if balance <= 0:
        raise ValueError("balance phải > 0")
    if atr <= 0:
        raise ValueError("ATR phải > 0")
    if atr_stop_mult <= 0:
        raise ValueError("atr_stop_mult phải > 0")

    risk_usdt = balance * (risk_per_trade_pct / 100.0)
    stop_distance = atr * atr_stop_mult
    quantity = risk_usdt / stop_distance
    return quantity, risk_usdt, stop_distance
