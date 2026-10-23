"""STL / TP / R:R theo thesis S/D (gợi ý — không tự vào lệnh)."""

from __future__ import annotations

from .zones import Zone


def stop_level(side: str, zone: Zone) -> float:
    """
    STL = mép hết vùng (invalidation).
    Vùng Mua → đáy vùng (bot). Vùng Bán → đỉnh vùng (top).
    """
    return zone.bot if side == "buy" else zone.top


def next_target(side: str, price: float, zones_same_tf: list[Zone]) -> Zone | None:
    """
    TP thô: vùng đối ứng gần nhất cùng khung.
    MUA → Vùng Bán gần nhất phía trên giá.
    BÁN → Vùng Mua gần nhất phía dưới giá.
    """
    if side == "buy":
        cands = [z for z in zones_same_tf if z.side == "sell" and z.bot > price]
        if not cands:
            return None
        return min(cands, key=lambda z: z.bot)
    cands = [z for z in zones_same_tf if z.side == "buy" and z.top < price]
    if not cands:
        return None
    return max(cands, key=lambda z: z.top)


def take_profit_price(side: str, target: Zone) -> float:
    """Mép vào của vùng đối ứng (chạm Supply/Demand đối diện)."""
    return target.bot if side == "buy" else target.top


def risk_reward(entry: float, stl: float, tp: float | None) -> float | None:
    if tp is None:
        return None
    risk = abs(entry - stl)
    if risk <= 0:
        return None
    reward = abs(tp - entry)
    return round(reward / risk, 2)
