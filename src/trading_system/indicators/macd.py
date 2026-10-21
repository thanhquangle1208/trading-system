"""MACD (12, 26, 9) chuẩn."""

from __future__ import annotations

from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles
from trading_system.indicators.utils import closes, ema, last_number


class Macd(IndicatorPlugin):
    id = "macd"
    display_name = "MACD"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        fast = int(params.get("fast", 12))
        slow = int(params.get("slow", 26))
        signal_period = int(params.get("signal", 9))
        need = slow + signal_period
        require_min_candles(candles, need, self.display_name)

        c = closes(candles)
        ema_fast = ema(c, fast)
        ema_slow = ema(c, slow)
        macd_line: list[float | None] = [None] * len(c)
        for i in range(len(c)):
            if ema_fast[i] is not None and ema_slow[i] is not None:
                macd_line[i] = float(ema_fast[i]) - float(ema_slow[i])

        # Signal = EMA của macd_line (bỏ None đầu)
        macd_vals = [v for v in macd_line if v is not None]
        signal_raw = ema(macd_vals, signal_period)
        signal_line: list[float | None] = [None] * len(c)
        hist: list[float | None] = [None] * len(c)
        # map signal_raw back: first non-None macd index
        first_macd_idx = next(i for i, v in enumerate(macd_line) if v is not None)
        for j, s in enumerate(signal_raw):
            idx = first_macd_idx + j
            if idx >= len(c):
                break
            signal_line[idx] = s
            if s is not None and macd_line[idx] is not None:
                hist[idx] = float(macd_line[idx]) - float(s)

        m = last_number(macd_line)
        s = last_number(signal_line)
        h = last_number(hist)
        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={"macd": m, "signal": s, "histogram": h},
            series={"macd": macd_line, "signal": signal_line, "histogram": hist},
            signals={
                "macd_above_signal": m is not None and s is not None and m > s,
                "hist_positive": h is not None and h > 0,
            },
        )
