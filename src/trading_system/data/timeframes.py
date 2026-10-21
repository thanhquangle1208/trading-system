"""Chuẩn hóa khung thời gian nội bộ ↔ ccxt."""

from __future__ import annotations

# Nội bộ: M15, H1, H4, D1  →  ccxt: 15m, 1h, 4h, 1d
_TO_CCXT = {
    "M15": "15m",
    "H1": "1h",
    "H4": "4h",
    "D1": "1d",
    "15m": "15m",
    "1h": "1h",
    "4h": "4h",
    "1d": "1d",
}


def to_ccxt_timeframe(tf: str) -> str:
    key = tf.strip()
    if key not in _TO_CCXT:
        raise ValueError(f"Timeframe không hỗ trợ: {tf!r}. Dùng M15/H1/H4/D1.")
    return _TO_CCXT[key]
