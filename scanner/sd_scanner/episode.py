"""Chống spam theo nhịp (episode) + cooldown + hysteresis mép vùng."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .zones import Zone, depth_band, penetration, price_in_zone


def zone_key(symbol: str, tf: str, zone: Zone) -> str:
    return f"{symbol}|{tf}|{zone.side}|{zone.pivot_time}|{round(zone.top, 6)}|{round(zone.bot, 6)}"


def side_key(symbol: str, side: str) -> str:
    return f"{symbol}|{side}"


@dataclass
class EpisodeState:
    """
    - Vào vùng: giá trong [bot, top].
    - Thoát nhịp: ra ngoài + đệm.
    - Cooldown theo vùng + theo cặp/chiều.
    - min_band: bỏ báo band 1 (mới chạm mép) nếu >= 2.
    """

    cooldown_sec: int = 1800
    side_cooldown_sec: int = 3600
    exit_pad_frac: float = 0.03
    min_band: int = 2

    alerted_band: dict[str, int] = field(default_factory=dict)
    inside: dict[str, bool] = field(default_factory=dict)
    last_alert_ts: dict[str, float] = field(default_factory=dict)
    last_side_alert_ts: dict[str, float] = field(default_factory=dict)

    def on_price(
        self,
        symbol: str,
        tf: str,
        zone: Zone,
        price: float,
        *,
        emit: bool = True,
    ) -> int | None:
        """
        emit=False: chỉ cập nhật trong/ngoài vùng (không báo).
        emit=True: có thể trả band để gửi Telegram.
        """
        key = zone_key(symbol, tf, zone)
        was_inside = self.inside.get(key, False)

        strictly_in = price_in_zone(price, zone, pad_frac=0.0)
        if was_inside:
            still_near = price_in_zone(price, zone, pad_frac=self.exit_pad_frac)
            if not still_near:
                self.inside[key] = False
                self.alerted_band.pop(key, None)
                return None
        else:
            if not strictly_in:
                return None

        self.inside[key] = True
        if not strictly_in or not emit:
            return None

        pen = penetration(price, zone)
        band = depth_band(pen)
        if band < self.min_band:
            return None

        prev = self.alerted_band.get(key, 0)
        if band <= prev:
            return None

        now = time.time()
        last = self.last_alert_ts.get(key, 0.0)
        if now - last < self.cooldown_sec:
            return None

        sk = side_key(symbol, zone.side)
        last_side = self.last_side_alert_ts.get(sk, 0.0)
        if now - last_side < self.side_cooldown_sec:
            return None

        self.alerted_band[key] = band
        self.last_alert_ts[key] = now
        self.last_side_alert_ts[sk] = now
        return band
