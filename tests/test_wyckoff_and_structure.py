from __future__ import annotations

from trading_system.data.base import Candle
from trading_system.indicators.candles_patterns import CandlePatterns
from trading_system.indicators.market_structure import MarketStructure
from trading_system.indicators.support_resistance import SupportResistance
from trading_system.indicators.volume import VolumeStats
from trading_system.indicators.wyckoff import WyckoffBasic


def _c(ts: int, o: float, h: float, l: float, c: float, v: float = 100.0) -> Candle:
    return Candle(ts, o, h, l, c, v)


def test_wyckoff_detects_spring() -> None:
    # Range ~100–110, nến cuối đâm xuống 98 rồi đóng 101
    candles = []
    for i in range(29):
        px = 100 + (i % 5)
        candles.append(_c(i, px, px + 2, px - 2, px, 100))
    # Force clear range high/low on base
    candles = [_c(i, 105, 110, 100, 105, 100) for i in range(29)]
    candles.append(_c(29, 102, 103, 97, 101, 200))  # spring
    result = WyckoffBasic().compute(candles, lookback=30, pierce_pct=0.002)
    assert result.signals["spring"] is True
    assert result.values["phase"] == "accumulation_spring"
    assert result.signals["bullish_bias"] is True


def test_wyckoff_detects_upthrust() -> None:
    candles = [_c(i, 105, 110, 100, 105, 100) for i in range(29)]
    candles.append(_c(29, 108, 113, 107, 109, 200))  # upthrust above 110, close back
    result = WyckoffBasic().compute(candles, lookback=30, pierce_pct=0.002)
    assert result.signals["upthrust"] is True
    assert result.values["phase"] == "distribution_upthrust"


def test_bullish_engulfing() -> None:
    candles = [
        _c(1, 110, 111, 100, 101),  # bearish
        _c(2, 100, 112, 99, 111),  # bullish engulf
    ]
    result = CandlePatterns().compute(candles)
    assert result.signals["bullish_engulfing"] is True


def test_market_structure_uptrend() -> None:
    # nửa đầu thấp, nửa sau cao hơn cả high và low
    candles = [_c(i, 100, 102, 98, 100) for i in range(10)]
    candles += [_c(10 + i, 110, 115, 108, 112) for i in range(10)]
    result = MarketStructure().compute(candles, lookback=5)
    assert result.signals["uptrend"] is True


def test_support_resistance_window() -> None:
    candles = [_c(i, 100, 105, 95, 100) for i in range(25)]
    result = SupportResistance().compute(candles, lookback=20)
    assert result.values["resistance"] == 105
    assert result.values["support"] == 95


def test_volume_spike() -> None:
    candles = [_c(i, 100, 101, 99, 100, 100) for i in range(20)]
    candles[-1] = _c(19, 100, 101, 99, 100, 500)
    result = VolumeStats().compute(candles, period=20, spike_mult=1.5)
    assert result.signals["volume_spike"] is True
