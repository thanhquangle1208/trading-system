"""Chống spam theo nhịp (episode) + band độ sâu nội bộ."""

from __future__ import annotations

from dataclasses import dataclass, field

from .zones import Zone, depth_band, penetration, price_in_zone


def zone_key(symbol: str, tf: str, zone: Zone) -> str:
    return f"{symbol}|{tf}|{zone.side}|{zone.pivot_time}|{round(zone.top, 6)}|{round(zone.bot, 6)}"


@dataclass
class EpisodeState:
    # key → band cao nhất đã báo trong nhịp hiện tại (0 = chưa)
    alerted_band: dict[str, int] = field(default_factory=dict)
    # key đang trong zone?
    inside: dict[str, bool] = field(default_factory=dict)

    def on_price(self, symbol: str, tf: str, zone: Zone, price: float) -> int | None:
        """
        Trả band (1/2/3) nếu cần báo Telegram lần này; None nếu im.
        """
        key = zone_key(symbol, tf, zone)
        inside_now = price_in_zone(price, zone, pad_frac=0.02)

        if not inside_now:
            # thoát nhịp: xóa trạng thái để lần vào sau báo lại
            if self.inside.get(key):
                self.inside[key] = False
                self.alerted_band.pop(key, None)
            return None

        self.inside[key] = True
        pen = penetration(price, zone)
        band = depth_band(pen)
        prev = self.alerted_band.get(key, 0)
        if band > prev:
            self.alerted_band[key] = band
            return band
        return None
