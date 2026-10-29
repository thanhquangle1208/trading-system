"""STL / TP / R:R theo thesis S/D (gợi ý — không tự vào lệnh)."""

from __future__ import annotations

from .zones import Zone

# Khoảng cách tối thiểu Entry → STL (Tomas chốt 2.5%).
DEFAULT_MIN_STL_PCT = 0.025


def stop_level(
    side: str,
    zone: Zone,
    entry: float | None = None,
    *,
    min_stl_pct: float = DEFAULT_MIN_STL_PCT,
) -> float:
    """
    STL mặc định = mép hết vùng (MUA→bot, BÁN→top).

    Nếu Entry sát / trùng mép đó (khoảng cách < min_stl_pct, mặc định 2.5%),
    đẩy STL ra ngoài để luôn có ít nhất min_stl_pct risk — tránh Entry = STL.

    Nếu Entry còn đủ xa mép vùng → giữ nguyên mép vùng.
    """
    natural = zone.bot if side == "buy" else zone.top
    if entry is None or entry <= 0 or min_stl_pct <= 0:
        return natural

    if side == "buy":
        # Risk = entry - stl (STL phải dưới entry)
        gap_pct = (entry - natural) / entry
        if gap_pct >= min_stl_pct:
            return natural
        return entry * (1.0 - min_stl_pct)

    # sell: STL trên entry
    gap_pct = (natural - entry) / entry
    if gap_pct >= min_stl_pct:
        return natural
    return entry * (1.0 + min_stl_pct)


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
