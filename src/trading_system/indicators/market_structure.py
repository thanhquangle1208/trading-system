"""Cấu trúc thị trường đơn giản: HH/HL vs LH/LL trên cửa sổ swing."""

from __future__ import annotations

from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles
from trading_system.indicators.utils import highs, lows


class MarketStructure(IndicatorPlugin):
    id = "market_structure"
    display_name = "Market structure"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        lookback = int(params.get("lookback", 5))
        require_min_candles(candles, lookback * 4, self.display_name)
        h = highs(candles)
        l = lows(candles)

        # Hai đỉnh / hai đáy gần nhất theo cửa sổ không chồng
        mid = len(candles) // 2
        first_high = max(h[:mid])
        second_high = max(h[mid:])
        first_low = min(l[:mid])
        second_low = min(l[mid:])

        hh = second_high > first_high
        hl = second_low > first_low
        lh = second_high < first_high
        ll = second_low < first_low

        if hh and hl:
            structure = "uptrend"
        elif lh and ll:
            structure = "downtrend"
        else:
            structure = "range"

        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={
                "first_high": first_high,
                "second_high": second_high,
                "first_low": first_low,
                "second_low": second_low,
                "structure": structure,
            },
            signals={
                "uptrend": structure == "uptrend",
                "downtrend": structure == "downtrend",
                "range": structure == "range",
                "higher_high": hh,
                "higher_low": hl,
                "lower_high": lh,
                "lower_low": ll,
            },
        )
