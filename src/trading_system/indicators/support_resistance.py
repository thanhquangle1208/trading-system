"""Support / Resistance đơn giản từ high/low gần đây."""

from __future__ import annotations

from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles
from trading_system.indicators.utils import highs, lows


class SupportResistance(IndicatorPlugin):
    id = "support_resistance"
    display_name = "Support/Resistance"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        lookback = int(params.get("lookback", 20))
        require_min_candles(candles, lookback, self.display_name)
        window = candles[-lookback:]
        resistance = max(highs(window))
        support = min(lows(window))
        close = candles[-1].close
        mid = (resistance + support) / 2
        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={
                "support": support,
                "resistance": resistance,
                "mid": mid,
                "close": close,
                "lookback": lookback,
            },
            signals={
                "near_support": abs(close - support) / support < 0.005 if support else False,
                "near_resistance": abs(close - resistance) / resistance < 0.005 if resistance else False,
                "above_mid": close > mid,
            },
        )
