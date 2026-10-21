"""Paginate OHLCV helper — không gọi mạng trong unit test."""

from __future__ import annotations

from trading_system.data.ohlcv_history import fetch_ohlcv_paginated


class _FakeEx:
    rateLimit = 0

    def parse_timeframe(self, tf: str) -> float:
        assert tf == "1h"
        return 3600.0

    def milliseconds(self) -> int:
        return 1_700_000_000_000 + 500 * 3_600_000

    def fetch_ohlcv(self, symbol, timeframe="1h", since=None, limit=200):
        out = []
        t = since or 1_700_000_000_000
        for i in range(min(limit, 50)):
            px = 100 + i
            out.append([t + i * 3_600_000, px, px + 1, px - 1, px, 10.0])
        return out


def test_paginate_returns_candles() -> None:
    candles = fetch_ohlcv_paginated(_FakeEx(), "BTC/USDT", "H1", limit_bars=80, page_size=50)
    assert len(candles) >= 50
    assert candles[0].timestamp_ms < candles[-1].timestamp_ms
