"""RSI — Relative Strength Index (Wilder)."""

from __future__ import annotations

from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles
from trading_system.indicators.utils import closes, last_number


class Rsi(IndicatorPlugin):
    id = "rsi"
    display_name = "RSI"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        period = int(params.get("period", 14))
        overbought = float(params.get("overbought", 70))
        oversold = float(params.get("oversold", 30))
        require_min_candles(candles, period + 1, self.display_name)

        c = closes(candles)
        gains: list[float] = []
        losses: list[float] = []
        for i in range(1, len(c)):
            diff = c[i] - c[i - 1]
            gains.append(max(diff, 0.0))
            losses.append(max(-diff, 0.0))

        rsi_series: list[float | None] = [None] * len(c)
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        rsi_series[period] = _rsi_from_avg(avg_gain, avg_loss)

        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rsi_series[i + 1] = _rsi_from_avg(avg_gain, avg_loss)

        last = last_number(rsi_series)
        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={"rsi": last, "period": period},
            series={"rsi": rsi_series},
            signals={
                "overbought": last is not None and last >= overbought,
                "oversold": last is not None and last <= oversold,
            },
        )


def _rsi_from_avg(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))
