"""Test công thức chỉ báo trên dữ liệu cố định — không phụ thuộc sàn."""

from __future__ import annotations

from trading_system.data.base import Candle
from trading_system.indicators.atr import Atr
from trading_system.indicators.bollinger import BollingerBands
from trading_system.indicators.ema import Ema3489
from trading_system.indicators.macd import Macd
from trading_system.indicators.registry import get_indicator, list_indicators
from trading_system.indicators.rsi import Rsi
from trading_system.indicators.utils import ema, sma
from trading_system.indicators.vwap import Vwap


def _candles_from_closes(closes: list[float], vol: float = 100.0) -> list[Candle]:
    out: list[Candle] = []
    for i, c in enumerate(closes):
        out.append(
            Candle(
                timestamp_ms=1_700_000_000_000 + i * 60_000,
                open=c,
                high=c + 1,
                low=c - 1,
                close=c,
                volume=vol,
            )
        )
    return out


def test_sma_known() -> None:
    assert sma([1, 2, 3, 4, 5], 3) == [None, None, 2.0, 3.0, 4.0]


def test_ema_seed_and_rise() -> None:
    values = [10.0] * 5 + [20.0] * 5
    series = ema(values, 5)
    assert series[4] == 10.0
    assert series[-1] is not None and series[-1] > 10.0


def test_rsi_all_up_near_100() -> None:
    closes = [float(i) for i in range(1, 30)]
    result = Rsi().compute(_candles_from_closes(closes), period=14)
    assert result.values["rsi"] is not None
    assert result.values["rsi"] > 70


def test_rsi_flat_near_50() -> None:
    # xen kẽ lên xuống đều
    closes = [100.0, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100, 101, 100]
    result = Rsi().compute(_candles_from_closes(closes), period=14)
    rsi = result.values["rsi"]
    assert rsi is not None
    assert 40 <= rsi <= 60


def test_ema3489_bullish_on_uptrend() -> None:
    closes = [100.0 + i * 0.5 for i in range(100)]
    result = Ema3489().compute(_candles_from_closes(closes))
    assert result.signals["trend_bullish"] is True


def test_macd_runs() -> None:
    closes = [100.0 + (i % 7) for i in range(80)]
    result = Macd().compute(_candles_from_closes(closes))
    assert result.values["macd"] is not None
    assert result.values["signal"] is not None


def test_bollinger_contains_mid() -> None:
    closes = [100.0 + (i % 5) for i in range(40)]
    result = BollingerBands().compute(_candles_from_closes(closes), period=20)
    assert result.values["lower"] < result.values["middle"] < result.values["upper"]


def test_vwap_equals_typical_when_constant() -> None:
    candles = [
        Candle(1, 10, 12, 8, 11, 100),
        Candle(2, 10, 12, 8, 11, 100),
    ]
    # typical = (12+8+11)/3 = 10.333...
    result = Vwap().compute(candles)
    assert abs(result.values["vwap"] - (12 + 8 + 11) / 3) < 1e-9


def test_atr_positive() -> None:
    closes = [100.0 + i for i in range(30)]
    result = Atr().compute(_candles_from_closes(closes), period=14)
    assert result.values["atr"] is not None and result.values["atr"] > 0


def test_registry_lists_wyckoff() -> None:
    ids = list_indicators()
    assert "wyckoff_basic" in ids
    assert "ema_34_89" in ids
    plugin = get_indicator("rsi")
    assert plugin.id == "rsi"
