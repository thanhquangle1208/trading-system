"""Độ hấp dẫn + độ tin cậy (thang /10)."""

from __future__ import annotations

from .zones import Zone, penetration


def depth_score(price: float, zone: Zone) -> float:
    """Độ hấp dẫn theo độ sâu: ~6.0 (mép) → ~9.0 (sát STL)."""
    pen = penetration(price, zone)
    return round(6.0 + 3.0 * pen, 1)


def confidence_score(n_tf_aligned: int) -> float:
    """
    Số khung (cùng phía mua/bán) đang có giá trong vùng.
    1 → 5.5 | 2 → 7.0 | 3 → 8.5 | 4 → 9.5
    """
    table = {0: 4.0, 1: 5.5, 2: 7.0, 3: 8.5, 4: 9.5}
    n = max(0, min(4, n_tf_aligned))
    return table[n]


def side_label(side: str) -> str:
    return "Vùng Mua" if side == "buy" else "Vùng Bán"
