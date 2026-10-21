"""Interface chung cho mọi adapter sàn (CEX / sau này DEX)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Candle:
    """Một nến OHLCV."""

    timestamp_ms: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "timestamp_ms": self.timestamp_ms,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }


class ExchangeAdapter(ABC):
    """Mọi sàn (Bybit, sau Binance, DEX…) implement chung interface này."""

    name: str

    @abstractmethod
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 100,
    ) -> list[Candle]:
        """Lấy nến gần nhất. timeframe: M15/H1/H4/D1 hoặc 15m/1h/…"""

    @abstractmethod
    def fetch_ticker_price(self, symbol: str) -> float:
        """Giá gần nhất (last)."""

    def close(self) -> None:
        """Giải phóng kết nối nếu cần."""
        return None
