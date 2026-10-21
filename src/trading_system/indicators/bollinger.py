"""Bollinger Bands."""

from __future__ import annotations

import math
from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles
from trading_system.indicators.utils import closes, last_number, sma


class BollingerBands(IndicatorPlugin):
    id = "bollinger"
    display_name = "Bollinger Bands"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        period = int(params.get("period", 20))
        mult = float(params.get("mult", 2.0))
        require_min_candles(candles, period, self.display_name)
        c = closes(candles)
        mid = sma(c, period)
        upper: list[float | None] = [None] * len(c)
        lower: list[float | None] = [None] * len(c)
        for i in range(period - 1, len(c)):
            window = c[i - period + 1 : i + 1]
            mean = sum(window) / period
            var = sum((x - mean) ** 2 for x in window) / period
            std = math.sqrt(var)
            upper[i] = mean + mult * std
            lower[i] = mean - mult * std

        last_close = c[-1]
        u = last_number(upper)
        l = last_number(lower)
        m = last_number(mid)
        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={"middle": m, "upper": u, "lower": l, "close": last_close},
            series={"middle": mid, "upper": upper, "lower": lower},
            signals={
                "above_upper": u is not None and last_close > u,
                "below_lower": l is not None and last_close < l,
            },
        )
