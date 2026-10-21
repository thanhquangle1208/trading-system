"""Unit test Bybit adapter với fake ccxt exchange (không gọi mạng)."""

from __future__ import annotations

from trading_system.data.bybit import BybitCcxtAdapter


class _FakeExchange:
    def __init__(self) -> None:
        self.sandbox = False

    def set_sandbox_mode(self, enabled: bool) -> None:
        self.sandbox = enabled

    def fetch_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100):
        assert symbol == "BTC/USDT"
        assert timeframe == "1h"
        return [[1_700_000_000_000, 100.0, 110.0, 90.0, 105.0, 12.0]][:limit]

    def fetch_ticker(self, symbol: str):
        return {"last": 105.5, "symbol": symbol}

    def close(self) -> None:
        return None


def test_bybit_adapter_maps_ohlcv(monkeypatch) -> None:
    fake = _FakeExchange()

    def _fake_bybit(_cfg):
        return fake

    monkeypatch.setattr("trading_system.data.bybit.ccxt.bybit", _fake_bybit)

    adapter = BybitCcxtAdapter(api_key="k", api_secret="s", testnet=True)
    assert fake.sandbox is True

    candles = adapter.fetch_ohlcv("BTC/USDT", "H1", limit=1)
    assert len(candles) == 1
    assert candles[0].close == 105.0
    assert adapter.fetch_ticker_price("BTC/USDT") == 105.5
    adapter.close()
