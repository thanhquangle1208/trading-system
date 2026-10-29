"""Bias khung tuần (W1 EMA) — Nấc 1 siết độ tin cậy.

Luật nhẹ (Tomas OK 2026-10-28):
- Giá > EMA W1 → chỉ cho phép cảnh báo MUA
- Giá < EMA W1 → chỉ cho phép cảnh báo BÁN
- Mặc định EMA length = 34
"""

from __future__ import annotations

import pandas as pd


def ema_last(closes: pd.Series, length: int) -> float | None:
    """EMA cuối chuỗi close. Cần ≥ length nến."""
    if length < 1:
        return None
    s = closes.dropna()
    if len(s) < length:
        return None
    return float(s.ewm(span=length, adjust=False).mean().iloc[-1])


def bias_allows(side: str, price: float, ema: float) -> bool:
    """True nếu chiều MUA/BÁN khớp hướng giá vs EMA tuần."""
    if side == "buy":
        return price > ema
    if side == "sell":
        return price < ema
    return False


def bias_label(price: float, ema: float, length: int) -> str:
    """Chuỗi ngắn cho tin Telegram (tiếng Việt)."""
    if price > ema:
        return f"tăng (giá > EMA{length} W1)"
    if price < ema:
        return f"giảm (giá < EMA{length} W1)"
    return f"đi ngang (giá ≈ EMA{length} W1)"
