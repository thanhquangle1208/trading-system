"""
Wyckoff cơ bản (Phase 2) — không port full methodology.

- Xác định trading range (vùng giá) trên lookback
- Spring: đâm thủng đáy range rồi đóng lại trong range (dấu hiệu hấp thụ bán)
- Upthrust: đâm thủng đỉnh range rồi đóng lại trong range
- Nhãn pha rất đơn giản: accumulation / distribution / trending / unclear
"""

from __future__ import annotations

from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles
from trading_system.indicators.utils import highs, lows, volumes


class WyckoffBasic(IndicatorPlugin):
    id = "wyckoff_basic"
    display_name = "Wyckoff cơ bản"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        lookback = int(params.get("lookback", 30))
        pierce_pct = float(params.get("pierce_pct", 0.002))  # 0.2%
        require_min_candles(candles, lookback, self.display_name)

        window = list(candles[-lookback:])
        # Range từ gần như toàn bộ cửa sổ trừ nến cuối (để so spring/upthrust)
        base = window[:-1]
        range_high = max(highs(base))
        range_low = min(lows(base))
        last = window[-1]
        close = last.close

        # Spring: low xuyên dưới range_low, close quay lại trên range_low
        spring = (
            last.low < range_low * (1 - pierce_pct)
            and close >= range_low
        )
        # Upthrust: high xuyên trên range_high, close quay lại dưới range_high
        upthrust = (
            last.high > range_high * (1 + pierce_pct)
            and close <= range_high
        )

        inside = range_low <= close <= range_high
        vol = volumes(window)
        avg_vol = sum(vol[:-1]) / max(len(vol) - 1, 1)
        vol_climax = last.volume >= avg_vol * 1.5

        # Pha đơn giản
        if spring:
            phase = "accumulation_spring"
        elif upthrust:
            phase = "distribution_upthrust"
        elif inside and abs(range_high - range_low) / range_low < 0.08:
            # Range hẹp tương đối → nghiêng sideways
            phase = "ranging"
        elif close > range_high:
            phase = "markup_or_breakout"
        elif close < range_low:
            phase = "markdown_or_breakdown"
        else:
            phase = "unclear"

        bias = "bullish" if spring or phase == "markup_or_breakout" else (
            "bearish" if upthrust or phase == "markdown_or_breakdown" else "neutral"
        )

        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={
                "range_high": range_high,
                "range_low": range_low,
                "close": close,
                "phase": phase,
                "bias": bias,
                "lookback": lookback,
            },
            signals={
                "spring": spring,
                "upthrust": upthrust,
                "in_range": inside,
                "volume_climax": vol_climax,
                "bullish_bias": bias == "bullish",
                "bearish_bias": bias == "bearish",
            },
        )
