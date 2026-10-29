"""STL: mọi lệnh Entry→STL ≥ 2.5%; mép vùng chỉ khi đã đủ xa."""

from __future__ import annotations

from sd_scanner.levels import enforce_min_stl, risk_reward, stl_distance_pct, stop_level
from sd_scanner.zones import Zone

PCT = 0.025


def test_buy_entry_equals_zone_bot_gets_buffer() -> None:
    z = Zone(side="buy", bot=129.4, top=131.7, pivot_time=1)
    stl = stop_level("buy", z, entry=129.4, min_stl_pct=PCT)
    assert stl_distance_pct(129.4, stl) >= PCT - 1e-12
    assert abs(stl - 129.4 * (1 - PCT)) < 1e-9
    rr = risk_reward(129.4, stl, tp=140.0)
    assert rr is not None and rr < 100


def test_buy_zone_edge_beyond_2_5_pct_keeps_edge() -> None:
    z = Zone(side="buy", bot=100.0, top=110.0, pivot_time=1)
    entry = 108.0  # ~7.4% tới bot
    stl = stop_level("buy", z, entry=entry, min_stl_pct=PCT)
    assert stl == 100.0
    assert stl_distance_pct(entry, stl) >= PCT


def test_buy_tight_gap_always_at_least_2_5() -> None:
    z = Zone(side="buy", bot=0.09647, top=0.09901, pivot_time=1)
    entry = 0.09746  # ~1% tới bot
    stl = stop_level("buy", z, entry=entry, min_stl_pct=PCT)
    assert stl_distance_pct(entry, stl) >= PCT - 1e-12
    assert abs(stl - entry * (1 - PCT)) < 1e-12


def test_sell_entry_equals_zone_top_gets_buffer() -> None:
    z = Zone(side="sell", bot=100.0, top=105.0, pivot_time=1)
    stl = stop_level("sell", z, entry=105.0, min_stl_pct=PCT)
    assert stl_distance_pct(105.0, stl) >= PCT - 1e-12
    assert abs(stl - 105.0 * (1 + PCT)) < 1e-9


def test_enforce_never_below_min() -> None:
    # Giả sử ai đó đưa STL quá sát — clamp lại
    assert abs(enforce_min_stl("buy", 100.0, 99.0, min_stl_pct=PCT) - 97.5) < 1e-9
    assert abs(enforce_min_stl("sell", 100.0, 101.0, min_stl_pct=PCT) - 102.5) < 1e-9


def test_no_alert_geometry_under_2_5_pct() -> None:
    """Quét vài entry trong vùng — không case nào < 2.5%."""
    z = Zone(side="buy", bot=96.0, top=100.0, pivot_time=1)
    for entry in (96.0, 96.5, 97.0, 98.0, 99.0, 99.9, 100.0):
        stl = stop_level("buy", z, entry=entry, min_stl_pct=PCT)
        assert stl_distance_pct(entry, stl) + 1e-12 >= PCT, (entry, stl)
