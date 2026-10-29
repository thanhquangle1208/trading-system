"""STL buffer 2.5% — không để Entry = STL."""

from __future__ import annotations

from sd_scanner.levels import risk_reward, stop_level
from sd_scanner.zones import Zone


def test_buy_entry_equals_zone_bot_gets_buffer() -> None:
    # AAVE-like: Entry trùng đáy vùng
    z = Zone(side="buy", bot=129.4, top=131.7, pivot_time=1)
    stl = stop_level("buy", z, entry=129.4, min_stl_pct=0.025)
    assert stl < 129.4
    assert abs(stl - 129.4 * 0.975) < 1e-9
    rr = risk_reward(129.4, stl, tp=140.0)
    assert rr is not None and rr < 100  # không còn R:R ảo hàng trăm


def test_buy_far_from_bot_keeps_zone_edge() -> None:
    z = Zone(side="buy", bot=100.0, top=110.0, pivot_time=1)
    entry = 108.0  # còn ~7.4% tới bot → giữ mép
    stl = stop_level("buy", z, entry=entry, min_stl_pct=0.025)
    assert stl == 100.0


def test_buy_tight_gap_widens_stl() -> None:
    # CC-like: ~1% tới bot → nới lên 2.5%
    z = Zone(side="buy", bot=0.09647, top=0.09901, pivot_time=1)
    entry = 0.09746
    stl = stop_level("buy", z, entry=entry, min_stl_pct=0.025)
    assert stl == entry * 0.975
    assert (entry - stl) / entry >= 0.025 - 1e-12


def test_sell_entry_equals_zone_top_gets_buffer() -> None:
    z = Zone(side="sell", bot=100.0, top=105.0, pivot_time=1)
    stl = stop_level("sell", z, entry=105.0, min_stl_pct=0.025)
    assert stl > 105.0
    assert abs(stl - 105.0 * 1.025) < 1e-9
