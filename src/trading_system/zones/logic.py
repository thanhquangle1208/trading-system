"""Luật vào vùng, trễ 2%, và nến ngày đóng dưới mức vô hiệu.

Không gọi mạng. Không ghi Notion.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from zoneinfo import ZoneInfo

from trading_system.zones.models import BuyZone

DAY_MS = 86_400_000


class AlertKind(str, Enum):
    ENTRY = "entry"
    APPROACHING = "approaching"
    INVALIDATION = "invalidation"


@dataclass
class ZoneMemory:
    """Nhớ trên đĩa để khởi động lại không báo trùng."""

    inside: bool = False
    approach_armed: bool = True
    invalidation_level_key: str | None = None

    def to_json(self) -> dict[str, object]:
        return {
            "inside": self.inside,
            "approach_armed": self.approach_armed,
            "invalidation_level_key": self.invalidation_level_key,
        }

    @classmethod
    def from_json(cls, raw: object) -> ZoneMemory:
        if not isinstance(raw, dict):
            return cls()
        return cls(
            inside=bool(raw.get("inside", False)),
            approach_armed=bool(raw.get("approach_armed", True)),
            invalidation_level_key=_optional_str(raw.get("invalidation_level_key")),
        )


@dataclass(frozen=True)
class ZoneAlert:
    kind: AlertKind
    zone: BuyZone
    price: float
    daily_close: float | None = None


@dataclass(frozen=True)
class Decision:
    memory: ZoneMemory
    alerts: tuple[ZoneAlert, ...]


def level_key(value: float) -> str:
    text = f"{value:.8f}".rstrip("0").rstrip(".")
    return text or "0"


def outside_hysteresis(price: float, lower: float, upper: float, hysteresis: float) -> bool:
    """Giá đã ra khỏi vùng thêm ít nhất `hysteresis` (0.02 = 2%)."""
    margin = max(0.0, hysteresis)
    return price < lower * (1 - margin) or price > upper * (1 + margin)


def decide_zone(
    zone: BuyZone,
    memory: ZoneMemory,
    price: float,
    daily_close: float | None,
    *,
    hysteresis: float,
    approaching: float | None,
) -> Decision:
    """Một vùng, một lần chạy. `approaching` là tỷ lệ (0.03 = 3%) hoặc None = tắt."""
    lower, upper = zone.bounds()
    inside_now = lower <= price <= upper
    alerts: list[ZoneAlert] = []

    new_inside = memory.inside
    if memory.inside:
        if outside_hysteresis(price, lower, upper, hysteresis):
            new_inside = False
    elif inside_now:
        alerts.append(ZoneAlert(AlertKind.ENTRY, zone, price, daily_close))
        new_inside = True

    new_approach = memory.approach_armed
    if approaching is not None and approaching > 0:
        band_top = upper * (1 + approaching)
        if price > band_top:
            new_approach = True
        elif new_inside or (memory.inside and price <= band_top):
            # Đang trong vùng, hoặc vừa đi ra qua dải gần — không phải 'tiến gần từ trên'.
            new_approach = False
        elif upper < price <= band_top and memory.approach_armed and not memory.inside:
            alerts.append(ZoneAlert(AlertKind.APPROACHING, zone, price, daily_close))
            new_approach = False

    new_level = memory.invalidation_level_key
    if zone.invalidation is not None and daily_close is not None:
        key = level_key(zone.invalidation)
        if daily_close < zone.invalidation:
            if memory.invalidation_level_key != key:
                alerts.append(
                    ZoneAlert(AlertKind.INVALIDATION, zone, price, daily_close)
                )
                new_level = key
        else:
            # Nến ngày đóng lại phía trên mức → vùng còn hiệu lực, lần sau phá sẽ báo tiếp.
            new_level = None

    memory_out = ZoneMemory(
        inside=new_inside,
        approach_armed=new_approach,
        invalidation_level_key=new_level,
    )
    return Decision(memory=memory_out, alerts=tuple(alerts))


def to_local(now: datetime, tz_name: str) -> datetime:
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone(timedelta(hours=7))
    return now.astimezone(tz)


def digest_due(
    now: datetime,
    last_date: str | None,
    *,
    hour: int,
    minute: int,
    tz_name: str,
) -> str | None:
    """Ngày lịch Việt Nam nếu đã tới giờ bản tin và hôm nay chưa gửi. Ngược lại None."""
    local = to_local(now, tz_name)
    if (local.hour, local.minute) < (hour, minute):
        return None
    today = local.date().isoformat()
    if last_date == today:
        return None
    return today


def _optional_str(value: object) -> str | None:
    if value is None or value == "":
        return None
    return str(value)
