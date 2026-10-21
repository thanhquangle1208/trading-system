"""VWAP phiên đơn giản trên toàn bộ chuỗi nến đưa vào (không reset theo ngày — đủ Phase 2)."""

from __future__ import annotations

from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles
from trading_system.indicators.utils import last_number


class Vwap(IndicatorPlugin):
    id = "vwap"
    display_name = "VWAP"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        _ = params
        require_min_candles(candles, 1, self.display_name)
        series: list[float | None] = []
        cum_pv = 0.0
        cum_v = 0.0
        for c in candles:
            typical = (c.high + c.low + c.close) / 3.0
            cum_pv += typical * c.volume
            cum_v += c.volume
            series.append(cum_pv / cum_v if cum_v > 0 else None)

        v = last_number(series)
        last_close = candles[-1].close
        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={"vwap": v, "close": last_close},
            series={"vwap": series},
            signals={
                "above_vwap": v is not None and last_close > v,
                "below_vwap": v is not None and last_close < v,
            },
        )
