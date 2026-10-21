"""
Chỗ cắm DEX (Uniswap / DEX khác) — KHÔNG dùng ccxt.

Phase 1: chỉ interface + NotImplemented.
Khi Tomas ưu tiên DEX: implement class thật, cùng ExchangeAdapter.
"""

from __future__ import annotations

from trading_system.data.base import Candle, ExchangeAdapter


class DexAdapterPlaceholder(ExchangeAdapter):
    """Placeholder — raise rõ ràng nếu gọi nhầm sớm."""

    name = "dex_placeholder"

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[Candle]:
        raise NotImplementedError(
            "DEX adapter chưa implement. Phase 1 chỉ để chỗ cắm. "
            f"(symbol={symbol}, timeframe={timeframe}, limit={limit})"
        )

    def fetch_ticker_price(self, symbol: str) -> float:
        raise NotImplementedError(
            f"DEX adapter chưa implement (symbol={symbol})."
        )
