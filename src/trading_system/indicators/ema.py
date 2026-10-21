"""EMA 34 / 89 — đường trung bình mũ."""

from __future__ import annotations

from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles
from trading_system.indicators.utils import closes, ema, last_number


class Ema3489(IndicatorPlugin):
    id = "ema_34_89"
    display_name = "EMA 34/89"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        fast = int(params.get("fast", 34))
        slow = int(params.get("slow", 89))
        require_min_candles(candles, slow, self.display_name)
        c = closes(candles)
        ema_fast = ema(c, fast)
        ema_slow = ema(c, slow)
        f = last_number(ema_fast)
        s = last_number(ema_slow)
        bullish = f is not None and s is not None and f > s
        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={"ema_fast": f, "ema_slow": s, "fast_period": fast, "slow_period": slow},
            series={"ema_fast": ema_fast, "ema_slow": ema_slow},
            signals={"trend_bullish": bullish, "trend_bearish": bool(f and s and f < s)},
        )
