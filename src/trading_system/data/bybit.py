"""Adapter Bybit qua ccxt — chỉ đọc dữ liệu ở Phase 1."""

from __future__ import annotations

from typing import Any

import ccxt

from trading_system.data.base import Candle, ExchangeAdapter
from trading_system.data.timeframes import to_ccxt_timeframe
from trading_system.logging_setup import get_logger

log = get_logger("data.bybit")


class BybitCcxtAdapter(ExchangeAdapter):
    name = "bybit"

    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        testnet: bool = True,
    ) -> None:
        options: dict[str, Any] = {"defaultType": "spot"}
        self._exchange = ccxt.bybit(
            {
                "apiKey": api_key or None,
                "secret": api_secret or None,
                "enableRateLimit": True,
                "options": options,
            }
        )
        if testnet:
            self._exchange.set_sandbox_mode(True)
        log.info(
            "Bybit adapter khởi tạo (testnet=%s, có_key=%s)",
            testnet,
            bool(api_key and api_secret),
        )

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[Candle]:
        # limit lớn → paginate (backtest)
        if limit > 200:
            from trading_system.data.ohlcv_history import fetch_ohlcv_paginated

            candles = fetch_ohlcv_paginated(
                self._exchange, symbol, timeframe, limit_bars=limit
            )
            log.debug("Bybit OHLCV paginated %s → %d nến", symbol, len(candles))
            return candles

        tf = to_ccxt_timeframe(timeframe)
        raw = self._exchange.fetch_ohlcv(symbol, timeframe=tf, limit=limit)
        candles = [
            Candle(
                timestamp_ms=int(row[0]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
            for row in raw
        ]
        log.debug("Bybit OHLCV %s %s → %d nến", symbol, tf, len(candles))
        return candles

    def fetch_ticker_price(self, symbol: str) -> float:
        ticker = self._exchange.fetch_ticker(symbol)
        last = ticker.get("last")
        if last is None:
            raise RuntimeError(f"Bybit không trả last price cho {symbol}")
        return float(last)

    def close(self) -> None:
        close_fn = getattr(self._exchange, "close", None)
        if callable(close_fn):
            close_fn()
