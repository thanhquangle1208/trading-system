"""Volume — so sánh khối lượng với trung bình."""

from __future__ import annotations

from typing import Any, Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorPlugin, IndicatorResult, require_min_candles
from trading_system.indicators.utils import last_number, sma, volumes


class VolumeStats(IndicatorPlugin):
    id = "volume"
    display_name = "Volume"

    def compute(self, candles: Sequence[Candle], **params: Any) -> IndicatorResult:
        period = int(params.get("period", 20))
        spike_mult = float(params.get("spike_mult", 1.5))
        require_min_candles(candles, period, self.display_name)
        vol = volumes(candles)
        avg = sma(vol, period)
        last_vol = vol[-1]
        last_avg = last_number(avg)
        spike = last_avg is not None and last_vol >= last_avg * spike_mult
        return IndicatorResult(
            indicator_id=self.id,
            display_name=self.display_name,
            values={"volume": last_vol, "avg_volume": last_avg, "period": period},
            series={"volume": [float(v) for v in vol], "avg_volume": avg},
            signals={"volume_spike": spike},
        )
