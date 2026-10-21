"""ATR — Average True Range (Wilder)."""

from __future__ import annotations

from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles
from trading_system.indicators.utils import last_number, true_ranges


class Atr(IndicatorPlugin):
    id = "atr"
    display_name = "ATR"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        period = int(params.get("period", 14))
        require_min_candles(candles, period + 1, self.display_name)
        trs = true_ranges(candles)
        atr_series: list[float | None] = [None] * len(candles)
        atr = sum(trs[1 : period + 1]) / period
        atr_series[period] = atr
        for i in range(period + 1, len(trs)):
            atr = (atr * (period - 1) + trs[i]) / period
            atr_series[i] = atr

        last = last_number(atr_series)
        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={"atr": last, "period": period},
            series={"atr": atr_series},
            signals={},
        )
