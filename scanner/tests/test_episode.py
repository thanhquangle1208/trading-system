"""Chống spam episode + persist đĩa."""

from __future__ import annotations

from pathlib import Path

from sd_scanner.episode import EpisodeState, side_key
from sd_scanner.zones import Zone


def _zone(bot: float = 10.0, top: float = 12.0) -> Zone:
    return Zone(side="buy", bot=bot, top=top, pivot_time=1_700_000_000_000)


def test_one_alert_per_zone_episode(tmp_path: Path) -> None:
    st = EpisodeState(
        cooldown_sec=1800,
        side_cooldown_sec=3600,
        min_band=2,
        state_path=tmp_path / "ep.json",
    )
    z = _zone()
    # Giữa vùng → band 2
    b1 = st.on_price("MONUSDT", "D1", z, 11.0, emit=True)
    assert b1 is not None
    # Cùng vùng, sâu hơn / giá lệch nhẹ → không báo lần 2
    b2 = st.on_price("MONUSDT", "D1", z, 10.5, emit=True)
    assert b2 is None


def test_side_cooldown_survives_restart(tmp_path: Path) -> None:
    path = tmp_path / "ep.json"
    z = _zone()
    st1 = EpisodeState(cooldown_sec=60, side_cooldown_sec=3600, min_band=2, state_path=path)
    assert st1.on_price("MONUSDT", "D1", z, 11.0, emit=True) is not None
    assert path.is_file()

    # “Restart”: object mới, nạp đĩa — side cooldown vẫn chặn
    st2 = EpisodeState(cooldown_sec=60, side_cooldown_sec=3600, min_band=2, state_path=path)
    st2.load()
    z2 = _zone(bot=10.5, top=12.5)  # vùng D1 đổi biên nhẹ sau rebuild
    assert st2.on_price("MONUSDT", "D1", z2, 11.2, emit=True) is None
    assert side_key("MONUSDT", "buy") in st2.last_side_alert_ts
