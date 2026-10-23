"""Chống spam theo nhịp (episode) + cooldown + hysteresis mép vùng."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .zones import Zone, depth_band, penetration, price_in_zone


def zone_key(symbol: str, tf: str, zone: Zone) -> str:
    return f"{symbol}|{tf}|{zone.side}|{zone.pivot_time}|{round(zone.top, 6)}|{round(zone.bot, 6)}"


@dataclass
class EpisodeState:
    """
    - Vào vùng: giá phải nằm **trong** [bot, top] (không đệm).
    - Thoát nhịp: chỉ khi giá ra **ngoài** thêm đệm (tránh lắc mép reset nhịp).
    - Cooldown: sau mỗi lần báo, cùng key im ít nhất N giây.
    """

    cooldown_sec: int = 300  # 5 phút
    exit_pad_frac: float = 0.03  # ra xa 3% chiều cao vùng mới hết nhịp

    alerted_band: dict[str, int] = field(default_factory=dict)
    inside: dict[str, bool] = field(default_factory=dict)
    last_alert_ts: dict[str, float] = field(default_factory=dict)

    def on_price(self, symbol: str, tf: str, zone: Zone, price: float) -> int | None:
        """Trả band (1/2/3) nếu cần báo Telegram; None nếu im."""
        key = zone_key(symbol, tf, zone)
        was_inside = self.inside.get(key, False)

        strictly_in = price_in_zone(price, zone, pad_frac=0.0)
        # Đang trong nhịp thì chỉ thoát khi ra ngoài đệm (hysteresis)
        if was_inside:
            still_near = price_in_zone(price, zone, pad_frac=self.exit_pad_frac)
            if not still_near:
                self.inside[key] = False
                self.alerted_band.pop(key, None)
                return None
            inside_now = True
        else:
            # Chưa trong nhịp: chỉ bắt đầu khi thật sự trong vùng
            if not strictly_in:
                return None
            inside_now = True

        self.inside[key] = inside_now
        pen = penetration(price, zone)
        # Nếu giá hơi ngoài mép nhưng vẫn trong hysteresis (was_inside), không báo mới
        if not strictly_in:
            return None

        band = depth_band(pen)
        prev = self.alerted_band.get(key, 0)
        if band <= prev:
            return None

        now = time.time()
        last = self.last_alert_ts.get(key, 0.0)
        if now - last < self.cooldown_sec:
            return None

        self.alerted_band[key] = band
        self.last_alert_ts[key] = now
        return band
