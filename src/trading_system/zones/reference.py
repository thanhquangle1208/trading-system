"""Đọc cột 'Chuỗi/sàn tham chiếu' để chọn sàn và cặp."""

from __future__ import annotations

import re
from dataclasses import dataclass

_QUOTES = ("USDT", "USDC", "BUSD", "USD")
_SYMBOL_RE = re.compile(r"\b([A-Z0-9]{2,15})(?:[/\-])?(USDT|USDC|BUSD|USD)\b")


@dataclass(frozen=True)
class PriceTarget:
    ticker: str
    venue: str | None
    symbol: str
    market: str  # spot | perp

    def label(self) -> str:
        where = self.venue or "mặc định"
        return f"{where} {self.market} {self.symbol}"


def parse_reference(text: str, ticker: str) -> PriceTarget:
    ticker = _clean_ticker(ticker)
    upper = (text or "").upper()
    venue: str | None = None
    if "BYBIT" in upper:
        venue = "bybit"
    elif "BINANCE" in upper:
        venue = "binance"
    elif "OKX" in upper or "OKEX" in upper:
        venue = "okx"
    market = "spot"
    if any(word in upper for word in ("PERP", "FUTURE", "HỢP ĐỒNG", "LINEAR", "SWAP")):
        market = "perp"
    match = _SYMBOL_RE.search(upper)
    if match:
        symbol = f"{match.group(1)}{match.group(2)}"
    elif ticker:
        symbol = f"{ticker}USDT"
    else:
        symbol = ""
    return PriceTarget(ticker=ticker, venue=venue, symbol=symbol, market=market)


def _clean_ticker(raw: str) -> str:
    text = (raw or "").strip().upper().replace("$", "")
    if "/" in text:
        text = text.split("/", 1)[0]
    return re.sub(r"[^A-Z0-9]", "", text)
