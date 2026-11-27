"""Luật vào vùng, trễ, vô hiệu, và câu chữ tiếng Việt."""

from __future__ import annotations

from datetime import datetime, timezone

from trading_system.zones.logic import (
    AlertKind,
    ZoneMemory,
    decide_zone,
    digest_due,
    outside_hysteresis,
)
from trading_system.zones.messages import (
    format_digest,
    format_entry,
    format_invalidation,
    format_price,
)
from trading_system.zones.models import STATUS_EXPIRED, STATUS_STALE, BuyZone


def _zone(**overrides) -> BuyZone:
    data = dict(
        page_id="page-btc-1",
        token_name="Bitcoin",
        ticker="BTC",
        zone_no="1",
        lower=55_000.0,
        upper=61_000.0,
        invalidation=53_000.0,
        status="Đang theo dõi",
        reference="Spot / Binance BTCUSDT",
        note="chờ nến xác nhận",
        link="https://www.notion.so/btc-zone",
    )
    data.update(overrides)
    return BuyZone(**data)


def test_format_price_vietnamese() -> None:
    assert format_price(55_000) == "55.000"
    assert format_price(60_850) == "60.850"
    assert format_price(52_700) == "52.700"
    assert format_price(53_000) == "53.000"
    assert format_price(25.5) == "25,5"
    assert format_price(0.00125) == "0,00125"


def test_entry_message_matches_example() -> None:
    text = format_entry(_zone(), 60_850)
    assert text == (
        "🟢 BTC vào Vùng 1 (55.000–61.000). Giá hiện tại: 60.850. "
        "Vô hiệu nếu nến ngày đóng dưới 53.000. "
        "Ghi chú: chờ nến xác nhận "
        "https://www.notion.so/btc-zone"
    )


def test_entry_message_omits_missing_invalidation_note_and_link() -> None:
    text = format_entry(_zone(invalidation=None, note="  ", link=""), 60_850)
    assert "Vô hiệu" not in text
    assert "Ghi chú" not in text
    assert "http" not in text
    assert "60.850" in text


def test_invalidation_message_matches_example() -> None:
    text = format_invalidation(_zone(link=""), 52_700)
    assert text == (
        "🔴 BTC – Vùng 1 hết hiệu lực: nến ngày đóng 52.700 < 53.000. "
        "Dừng mua vùng này, đánh giá lại."
    )


def test_entry_once_then_hysteresis_rearms() -> None:
    zone = _zone()
    memory = ZoneMemory()
    first = decide_zone(zone, memory, 60_850, None, hysteresis=0.02, approaching=None)
    assert [a.kind for a in first.alerts] == [AlertKind.ENTRY]
    assert first.memory.inside is True

    still = decide_zone(zone, first.memory, 60_000, None, hysteresis=0.02, approaching=None)
    assert still.alerts == ()
    assert still.memory.inside is True

    # 1% phía trên mép — vẫn trong dải trễ, không báo lại, chưa cài lại
    near = decide_zone(zone, still.memory, 61_000 * 1.01, None, hysteresis=0.02, approaching=None)
    assert near.alerts == ()
    assert near.memory.inside is True

    # Hơn 2% phía trên — cài lại, không báo
    left = decide_zone(zone, near.memory, 61_000 * 1.03, None, hysteresis=0.02, approaching=None)
    assert left.alerts == ()
    assert left.memory.inside is False

    again = decide_zone(zone, left.memory, 60_000, None, hysteresis=0.02, approaching=None)
    assert [a.kind for a in again.alerts] == [AlertKind.ENTRY]


def test_rearm_below_zone_by_more_than_two_percent() -> None:
    zone = _zone()
    inside = decide_zone(zone, ZoneMemory(), 56_000, None, hysteresis=0.02, approaching=None)
    slight = decide_zone(zone, inside.memory, 55_000 * 0.99, None, hysteresis=0.02, approaching=None)
    assert slight.memory.inside is True
    assert slight.alerts == ()
    far = decide_zone(zone, slight.memory, 55_000 * 0.97, None, hysteresis=0.02, approaching=None)
    assert far.memory.inside is False
    assert outside_hysteresis(55_000 * 0.97, 55_000, 61_000, 0.02)
    assert not outside_hysteresis(55_000 * 0.99, 55_000, 61_000, 0.02)


def test_approaching_off_by_default_and_on_when_configured() -> None:
    zone = _zone()
    above = 61_000 * 1.02
    off = decide_zone(zone, ZoneMemory(), above, None, hysteresis=0.02, approaching=None)
    assert off.alerts == ()

    armed = ZoneMemory(approach_armed=True)
    near = decide_zone(zone, armed, above, None, hysteresis=0.02, approaching=0.03)
    assert [a.kind for a in near.alerts] == [AlertKind.APPROACHING]
    assert near.memory.approach_armed is False

    again = decide_zone(zone, near.memory, above, None, hysteresis=0.02, approaching=0.03)
    assert again.alerts == ()

    # Ra hẳn phía trên dải 3% thì cài lại, lần sau vào dải sẽ báo tiếp
    far = 61_000 * 1.05
    rearmed = decide_zone(zone, again.memory, far, None, hysteresis=0.02, approaching=0.03)
    assert rearmed.memory.approach_armed is True
    back = decide_zone(zone, rearmed.memory, above, None, hysteresis=0.02, approaching=0.03)
    assert [a.kind for a in back.alerts] == [AlertKind.APPROACHING]


def test_leaving_zone_upward_does_not_count_as_approaching() -> None:
    zone = _zone()
    inside = decide_zone(zone, ZoneMemory(), 60_000, None, hysteresis=0.02, approaching=0.05)
    # 3% trên vùng: đã ra khỏi dải trễ 2%, nhưng vẫn trong dải 'tiến gần' 5%
    left = decide_zone(zone, inside.memory, 61_000 * 1.03, None, hysteresis=0.02, approaching=0.05)
    assert left.alerts == ()
    assert left.memory.inside is False
    assert left.memory.approach_armed is False


def test_invalidation_once_until_daily_close_recovers() -> None:
    zone = _zone()
    first = decide_zone(zone, ZoneMemory(), 60_000, 52_700, hysteresis=0.02, approaching=None)
    kinds = [a.kind for a in first.alerts]
    assert AlertKind.INVALIDATION in kinds
    assert AlertKind.ENTRY in kinds

    second = decide_zone(zone, first.memory, 60_000, 52_000, hysteresis=0.02, approaching=None)
    assert AlertKind.INVALIDATION not in [a.kind for a in second.alerts]

    recovered = decide_zone(zone, second.memory, 60_000, 54_000, hysteresis=0.02, approaching=None)
    assert recovered.memory.invalidation_level_key is None

    broken = decide_zone(zone, recovered.memory, 60_000, 52_500, hysteresis=0.02, approaching=None)
    assert AlertKind.INVALIDATION in [a.kind for a in broken.alerts]


def test_missing_invalidation_does_not_block_entry() -> None:
    zone = _zone(invalidation=None)
    decision = decide_zone(zone, ZoneMemory(), 60_000, 1.0, hysteresis=0.02, approaching=None)
    assert [a.kind for a in decision.alerts] == [AlertKind.ENTRY]


def test_changed_invalidation_level_can_alert_again() -> None:
    zone = _zone(invalidation=53_000)
    first = decide_zone(zone, ZoneMemory(), 60_000, 52_000, hysteresis=0.02, approaching=None)
    moved = _zone(invalidation=51_000)
    again = decide_zone(moved, first.memory, 60_000, 50_000, hysteresis=0.02, approaching=None)
    assert AlertKind.INVALIDATION in [a.kind for a in again.alerts]


def test_digest_waits_until_0705_vietnam_and_once_per_day() -> None:
    before = datetime(2026, 11, 26, 23, 50, tzinfo=timezone.utc)  # 06:50 ngày 27 giờ VN
    assert digest_due(before, None, hour=7, minute=5, tz_name="Asia/Ho_Chi_Minh") is None

    at = datetime(2026, 11, 27, 0, 5, tzinfo=timezone.utc)  # 07:05 ngày 27
    assert digest_due(at, None, hour=7, minute=5, tz_name="Asia/Ho_Chi_Minh") == "2026-11-27"
    assert digest_due(at, "2026-11-27", hour=7, minute=5, tz_name="Asia/Ho_Chi_Minh") is None

    late = datetime(2026, 11, 27, 2, 0, tzinfo=timezone.utc)  # cron trễ tới 09:00 VN
    assert digest_due(late, None, hour=7, minute=5, tz_name="Asia/Ho_Chi_Minh") == "2026-11-27"

    nxt = datetime(2026, 11, 28, 0, 5, tzinfo=timezone.utc)
    assert digest_due(nxt, "2026-11-27", hour=7, minute=5, tz_name="Asia/Ho_Chi_Minh") == "2026-11-28"


def test_inactive_statuses_are_not_actionable() -> None:
    assert _zone(status=STATUS_EXPIRED).skip_reason()
    assert _zone(status=STATUS_STALE).skip_reason()
    assert _zone(status="").skip_reason()
    assert _zone(status="Đang theo dõi").skip_reason() is None


def test_missing_bounds_or_ticker_skipped() -> None:
    assert "Giá dưới" in (_zone(lower=None).skip_reason() or "")
    assert "Ticker" in (_zone(ticker="").skip_reason() or "")


def test_digest_lists_zones_and_empty_states() -> None:
    zone = _zone(link="")
    text = format_digest([(zone, 60_850, False)], [], hour=7, minute=5, watching=1)
    assert "BTC Vùng 1" in text
    assert "60.850" in text
    assert "55.000–61.000" in text
    empty = format_digest([], ["SECZ"], hour=7, minute=5, watching=1)
    assert "Không có giá nào đang nằm trong" in empty
    assert "SECZ" in empty
    none = format_digest([], [], hour=7, minute=5, watching=0)
    assert "Không có vùng nào ở trạng thái" in none
