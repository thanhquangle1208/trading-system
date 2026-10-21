"""Mẫu nến đơn giản: engulfing, pin bar (bóng dài)."""

from __future__ import annotations

from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles


class CandlePatterns(IndicatorPlugin):
    id = "candle_patterns"
    display_name = "Nến & pattern"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        _ = params
        require_min_candles(candles, 2, self.display_name)
        prev, cur = candles[-2], candles[-1]

        bull_engulf = (
            prev.close < prev.open
            and cur.close > cur.open
            and cur.open <= prev.close
            and cur.close >= prev.open
        )
        bear_engulf = (
            prev.close > prev.open
            and cur.close < cur.open
            and cur.open >= prev.close
            and cur.close <= prev.open
        )

        body = abs(cur.close - cur.open)
        upper_wick = cur.high - max(cur.open, cur.close)
        lower_wick = min(cur.open, cur.close) - cur.low
        range_ = cur.high - cur.low or 1e-9
        bull_pin = lower_wick > body * 2 and lower_wick / range_ > 0.6
        bear_pin = upper_wick > body * 2 and upper_wick / range_ > 0.6

        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={
                "body": body,
                "upper_wick": upper_wick,
                "lower_wick": lower_wick,
            },
            signals={
                "bullish_engulfing": bull_engulf,
                "bearish_engulfing": bear_engulf,
                "bullish_pin": bull_pin,
                "bearish_pin": bear_pin,
            },
        )
