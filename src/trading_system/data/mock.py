"""Adapter giả — không cần API key; dùng cho test và khi MOCK_EXCHANGE=true."""

from __future__ import annotations

from trading_system.data.base import Candle, ExchangeAdapter
from trading_system.data.timeframes import to_ccxt_timeframe
from trading_system.logging_setup import get_logger

log = get_logger("data.mock")

# Giá BTC giả định quanh 60_000 để paper/test ổn định
_BASE_PRICE = 60_000.0


class MockExchangeAdapter(ExchangeAdapter):
    name = "mock"

    def __init__(self, base_price: float = _BASE_PRICE) -> None:
        self.base_price = base_price
        log.info("Mock exchange sẵn sàng (base_price=%.2f)", base_price)

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[Candle]:
        _ = to_ccxt_timeframe(timeframe)  # validate
        candles: list[Candle] = []
        # timestamp giả: cách nhau 1 phút cho đơn giản trong mock
        start = 1_700_000_000_000
        for i in range(limit):
            px = self.base_price + (i % 10) * 5.0
            candles.append(
                Candle(
                    timestamp_ms=start + i * 60_000,
                    open=px,
                    high=px + 10,
                    low=px - 10,
                    close=px + 1,
                    volume=100.0 + i,
                )
            )
        log.debug("Mock OHLCV %s %s → %d nến", symbol, timeframe, len(candles))
        return candles

    def fetch_ticker_price(self, symbol: str) -> float:
        log.debug("Mock ticker %s → %.2f", symbol, self.base_price)
        return self.base_price
