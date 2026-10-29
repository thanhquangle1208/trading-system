"""STL / TP / R:R theo thesis S/D (gợi ý — không tự vào lệnh)."""

from __future__ import annotations

from .zones import Zone

# Khoảng cách tối thiểu Entry → STL (Tomas chốt: mọi lệnh ≥ 2.5%).
DEFAULT_MIN_STL_PCT = 0.025


def stl_distance_pct(entry: float, stl: float) -> float:
    """|Entry − STL| / Entry. Entry ≤ 0 → 0."""
    if entry <= 0:
        return 0.0
    return abs(entry - stl) / entry


def enforce_min_stl(
    side: str,
    entry: float,
    stl: float,
    *,
    min_stl_pct: float = DEFAULT_MIN_STL_PCT,
) -> float:
    """
    Bảo đảm STL cách Entry tối thiểu min_stl_pct.
    MUA: STL ≤ entry×(1−pct). BÁN: STL ≥ entry×(1+pct).
    """
    if entry <= 0 or min_stl_pct <= 0:
        return stl
    if side == "buy":
        floor = entry * (1.0 - min_stl_pct)  # STL không được cao hơn mức này
        return min(stl, floor)
    ceiling = entry * (1.0 + min_stl_pct)  # STL không được thấp hơn mức này
    return max(stl, ceiling)


def stop_level(
    side: str,
    zone: Zone,
    entry: float | None = None,
    *,
    min_stl_pct: float = DEFAULT_MIN_STL_PCT,
) -> float:
    """
    STL gợi ý:

    1) Ứng viên = mép hết vùng (MUA→bot / BÁN→top).
    2) Nếu mép vùng đã cách Entry ≥ min_stl_pct (2.5%) → dùng mép vùng.
    3) Nếu sát hơn 2.5% (hoặc trùng Entry) → đẩy STL ra ngoài đúng min_stl_pct.

    **Luật cứng:** không bao giờ trả STL với khoảng cách < min_stl_pct so với Entry
    (khi đã có entry hợp lệ).
    """
    natural = zone.bot if side == "buy" else zone.top
    if entry is None or entry <= 0:
        return natural

    # Prefer mép vùng nếu đã đủ xa; không thì mức 2.5%
    if side == "buy":
        min_dist_level = entry * (1.0 - min_stl_pct)  # xa nhất được phép về phía dưới = đủ 2.5%
        # natural đủ sâu dưới entry (≥ 2.5%) ↔ natural <= min_dist_level
        candidate = natural if natural <= min_dist_level else min_dist_level
    else:
        min_dist_level = entry * (1.0 + min_stl_pct)
        candidate = natural if natural >= min_dist_level else min_dist_level

    # Clamp lần cuối — không tin tưởng nhánh nào bỏ sót
    return enforce_min_stl(side, entry, candidate, min_stl_pct=min_stl_pct)


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
