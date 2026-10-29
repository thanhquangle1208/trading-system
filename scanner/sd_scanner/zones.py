"""Tính Vùng Mua / Vùng Bán — logic gần Thesis T3E (pivot + chạy xa + kill theo close)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import ZoneParams


@dataclass
class Zone:
    side: str  # "buy" | "sell"  → Vùng Mua / Vùng Bán
    top: float
    bot: float
    pivot_time: int  # ms

    @property
    def height(self) -> float:
        return max(self.top - self.bot, 1e-12)


def _atr(df: pd.DataFrame, length: int) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr.rolling(length, min_periods=length).mean()


def _find_pivots(series: pd.Series, left: int, right: int, mode: str) -> list[tuple[int, float]]:
    """Trả [(confirm_i, price_at_pivot_bar)] với pivot_bar = confirm_i - right."""
    vals = series.to_numpy()
    n = len(vals)
    found: list[tuple[int, float]] = []
    for i in range(left, n - right):
        window = vals[i - left : i + right + 1]
        pivot_price = vals[i]
        if mode == "low":
            ok = pivot_price == window.min()
        else:
            ok = pivot_price == window.max()
        if not ok:
            continue
        # tránh nhiều đáy bằng nhau: chỉ nhận nếu i là vị trí đầu tiên đạt min/max
        if mode == "low" and int(np.argmin(window)) != left:
            continue
        if mode == "high" and int(np.argmax(window)) != left:
            continue
        confirm_i = i + right
        if confirm_i < n:
            found.append((confirm_i, float(pivot_price)))
    return found


def build_zones(df: pd.DataFrame, params: ZoneParams) -> list[Zone]:
    """
    df columns: timestamp, open, high, low, close, volume (timestamp ms).
    Trả list zone còn sống tại nến cuối.
    """
    if df is None or len(df) < params.pivot_len * 2 + params.atr_len + 5:
        return []

    df = df.reset_index(drop=True)
    atr = _atr(df, params.atr_len)
    pl = params.pivot_len
    buys: list[Zone] = []
    sells: list[Zone] = []

    low_pivots = _find_pivots(df["low"], pl, pl, "low")
    high_pivots = _find_pivots(df["high"], pl, pl, "high")

    # Map confirm index → zone candidate; chỉ tạo khi tại confirm close chạy đủ xa
    for confirm_i, _ in low_pivots:
        pivot_i = confirm_i - pl
        if pivot_i < 0 or confirm_i >= len(df):
            continue
        a = atr.iloc[confirm_i]
        if pd.isna(a) or a <= 0:
            continue
        z_bot = float(df.loc[pivot_i, "low"])
        z_top = float(max(df.loc[pivot_i, "open"], df.loc[pivot_i, "close"]))
        if z_top <= z_bot:
            z_top = z_bot + float(a) * 0.15
        close_c = float(df.loc[confirm_i, "close"])
        if close_c >= z_top + float(a) * params.dep_atr:
            buys.append(
                Zone(
                    side="buy",
                    top=z_top,
                    bot=z_bot,
                    pivot_time=int(df.loc[pivot_i, "timestamp"]),
                )
            )

    for confirm_i, _ in high_pivots:
        pivot_i = confirm_i - pl
        if pivot_i < 0 or confirm_i >= len(df):
            continue
        a = atr.iloc[confirm_i]
        if pd.isna(a) or a <= 0:
            continue
        z_top = float(df.loc[pivot_i, "high"])
        z_bot = float(min(df.loc[pivot_i, "open"], df.loc[pivot_i, "close"]))
        if z_top <= z_bot:
            z_bot = z_top - float(a) * 0.15
        close_c = float(df.loc[confirm_i, "close"])
        if close_c <= z_bot - float(a) * params.dep_atr:
            sells.append(
                Zone(
                    side="sell",
                    top=z_top,
                    bot=z_bot,
                    pivot_time=int(df.loc[pivot_i, "timestamp"]),
                )
            )

    # Replay kill theo close (giống T3E: close thủng đáy mua / đỉnh bán)
    live_buys: list[Zone] = []
    live_sells: list[Zone] = []
    # Duyệt theo thời gian tạo; tại mỗi nến sau pivot, kill nếu close phá
    for z in buys:
        killed = False
        # tìm pivot row
        rows = df.index[df["timestamp"] == z.pivot_time]
        start = int(rows[0]) + 1 if len(rows) else 0
        for j in range(start, len(df)):
            if float(df.loc[j, "close"]) < z.bot:
                killed = True
                break
        if not killed:
            live_buys.append(z)

    for z in sells:
        killed = False
        rows = df.index[df["timestamp"] == z.pivot_time]
        start = int(rows[0]) + 1 if len(rows) else 0
        for j in range(start, len(df)):
            if float(df.loc[j, "close"]) > z.top:
                killed = True
                break
        if not killed:
            live_sells.append(z)

    # Giữ max_zones mới nhất (pivot_time lớn)
    live_buys.sort(key=lambda z: z.pivot_time)
    live_sells.sort(key=lambda z: z.pivot_time)
    live_buys = live_buys[-params.max_zones :]
    live_sells = live_sells[-params.max_zones :]
    return live_buys + live_sells


def penetration(price: float, zone: Zone) -> float:
    """0 = mới chạm mép ngoài, 1 = sát STL (đáy mua / đỉnh bán)."""
    h = zone.height
    if zone.side == "buy":
        # vào từ trên: top → bot
        p = (zone.top - price) / h
    else:
        p = (price - zone.bot) / h
    return float(min(1.0, max(0.0, p)))


def price_in_zone(price: float, zone: Zone, pad_frac: float = 0.0) -> bool:
    pad = zone.height * pad_frac
    return (zone.bot - pad) <= price <= (zone.top + pad)


def depth_band(pen: float) -> int:
    """1 / 2 / 3 — dùng nội bộ chống spam; không hiện L1/L2/L3 trên Telegram."""
    if pen < 0.33:
        return 1
    if pen < 0.67:
        return 2
    return 3
