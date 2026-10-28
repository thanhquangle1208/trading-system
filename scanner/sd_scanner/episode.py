"""Chống spam theo nhịp (episode) + cooldown + lưu đĩa (sống qua restart).

Lỗi đã gặp (MONUSDT 4 tin ~10′): state chỉ trong RAM → Mac auto-pull
restart scanner → quên cooldown → báo lại cùng cặp/vùng.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .zones import Zone, depth_band, penetration, price_in_zone

# Band tối đa (depth_band trả 1/2/3). Gán = max → không báo lại trong cùng nhịp.
_BAND_DONE = 3


def zone_key(symbol: str, tf: str, zone: Zone) -> str:
    return f"{symbol}|{tf}|{zone.side}|{zone.pivot_time}|{round(zone.top, 6)}|{round(zone.bot, 6)}"


def side_key(symbol: str, side: str) -> str:
    return f"{symbol}|{side}"


@dataclass
class EpisodeState:
    """
    - Vào vùng: giá trong [bot, top].
    - Thoát nhịp: ra ngoài + đệm → cho phép báo lại sau.
    - Cooldown theo vùng + theo cặp/chiều (bắt buộc lưu đĩa).
    - Mỗi vùng: chỉ **1 tin** trong một nhịp (không spam khi sâu thêm).
    - min_band: bỏ báo band 1 (mới chạm mép) nếu >= 2.
    """

    cooldown_sec: int = 1800
    side_cooldown_sec: int = 3600
    exit_pad_frac: float = 0.03
    min_band: int = 2
    state_path: Path | None = None

    alerted_band: dict[str, int] = field(default_factory=dict)
    inside: dict[str, bool] = field(default_factory=dict)
    last_alert_ts: dict[str, float] = field(default_factory=dict)
    last_side_alert_ts: dict[str, float] = field(default_factory=dict)

    def load(self) -> None:
        """Nạp cooldown từ đĩa (sau restart / auto-update)."""
        path = self.state_path
        if path is None or not path.is_file():
            return
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ! episode load: {e}")
            return
        self.alerted_band = {str(k): int(v) for k, v in (raw.get("alerted_band") or {}).items()}
        self.inside = {str(k): bool(v) for k, v in (raw.get("inside") or {}).items()}
        self.last_alert_ts = {str(k): float(v) for k, v in (raw.get("last_alert_ts") or {}).items()}
        self.last_side_alert_ts = {
            str(k): float(v) for k, v in (raw.get("last_side_alert_ts") or {}).items()
        }
        print(
            f"  episode: đã nạp state ({len(self.last_side_alert_ts)} side cooldown, "
            f"file={path})"
        )

    def save(self) -> None:
        path = self.state_path
        if path is None:
            return
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "alerted_band": self.alerted_band,
                "inside": self.inside,
                "last_alert_ts": self.last_alert_ts,
                "last_side_alert_ts": self.last_side_alert_ts,
                "saved_at": time.time(),
            }
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(path)
        except Exception as e:
            print(f"  ! episode save: {e}")

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
        dirty = False

        strictly_in = price_in_zone(price, zone, pad_frac=0.0)
        if was_inside:
            still_near = price_in_zone(price, zone, pad_frac=self.exit_pad_frac)
            if not still_near:
                self.inside[key] = False
                self.alerted_band.pop(key, None)
                self.save()
                return None
        else:
            if not strictly_in:
                return None

        if not self.inside.get(key, False):
            dirty = True
        self.inside[key] = True
        if not strictly_in or not emit:
            if dirty:
                self.save()
            return None

        pen = penetration(price, zone)
        band = depth_band(pen)
        if band < self.min_band:
            if dirty:
                self.save()
            return None

        # Đã báo 1 lần trong nhịp này → im (kể cả khi sâu hơn)
        prev = self.alerted_band.get(key, 0)
        if prev > 0:
            if dirty:
                self.save()
            return None

        now = time.time()
        last = self.last_alert_ts.get(key, 0.0)
        if now - last < self.cooldown_sec:
            if dirty:
                self.save()
            return None

        sk = side_key(symbol, zone.side)
        last_side = self.last_side_alert_ts.get(sk, 0.0)
        if now - last_side < self.side_cooldown_sec:
            if dirty:
                self.save()
            return None

        # Đánh dấu đã báo hết nhịp (không tăng band để spam lần 2)
        self.alerted_band[key] = _BAND_DONE
        self.last_alert_ts[key] = now
        self.last_side_alert_ts[sk] = now
        self.save()
        return band
