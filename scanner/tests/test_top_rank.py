""" /top — xếp hạng đa tiêu chí; pair chỉ soft bonus. """

from __future__ import annotations

from sd_scanner.alert_history import AlertRecord
from sd_scanner.top_rank import pair_soft_bonus, pick_top, score_alert


def _rec(
    symbol: str,
    *,
    confidence: float = 7.0,
    depth: float = 7.0,
    rr: float | None = 2.0,
    timeframe: str = "H4",
    w1_bias: str | None = "tăng",
    ts: float = 1_000.0,
) -> AlertRecord:
    return AlertRecord(
        ts=ts,
        symbol=symbol,
        timeframe=timeframe,
        side="buy",
        price=100.0,
        zone_bot=95.0,
        zone_top=102.0,
        stl=97.5,
        tp=110.0,
        rr=rr,
        depth=depth,
        confidence=confidence,
        w1_bias=w1_bias,
        message_id=1,
        chat_id="-100123",
    )


def test_one_per_pair_keeps_best() -> None:
    a = _rec("SOLUSDT", confidence=7.0, depth=7.0, ts=1)
    b = _rec("SOLUSDT", confidence=9.0, depth=8.0, ts=2)
    top = pick_top([a, b], limit=3)
    assert len(top) == 1
    assert top[0][0].confidence == 9.0


def test_alt_can_beat_btc_on_quality() -> None:
    """Pair soft không quyết định — alt điểm kỹ thuật cao vẫn thắng BTC yếu."""
    btc = _rec("BTCUSDT", confidence=7.0, depth=7.0, rr=1.5, timeframe="H4")
    alt = _rec("MONUSDT", confidence=9.5, depth=9.0, rr=4.0, timeframe="D1", w1_bias="tăng")
    top = pick_top([btc, alt], limit=3)
    assert top[0][0].symbol == "MONUSDT"
    assert score_alert(alt) > score_alert(btc)


def test_pair_soft_is_small() -> None:
    assert pair_soft_bonus("BTCUSDT") <= 1.5
    assert pair_soft_bonus("WEIRDCOINUSDT") >= 0.2
    # Chênh soft << một nấc confidence (1.0 * 3 = 3)
    assert pair_soft_bonus("BTCUSDT") - pair_soft_bonus("WEIRDCOINUSDT") < 3.0


def test_limit_three() -> None:
    recs = [
        _rec("BTCUSDT", confidence=9.0),
        _rec("ETHUSDT", confidence=8.5),
        _rec("SOLUSDT", confidence=8.0),
        _rec("AAVEUSDT", confidence=7.5),
    ]
    top = pick_top(recs, limit=3)
    assert len(top) == 3
    syms = {r.symbol for r, _ in top}
    assert "AAVEUSDT" not in syms
