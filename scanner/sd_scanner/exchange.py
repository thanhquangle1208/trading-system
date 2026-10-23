"""Lấy nến + giá Perp: Binance trước, thiếu cặp thì Bybit."""

from __future__ import annotations

import time
from typing import Any

import ccxt
import pandas as pd

TF_MAP = {
    "H1": "1h",
    "H4": "4h",
    "D1": "1d",
    "W1": "1w",
}


class MarketData:
    def __init__(self) -> None:
        self.binance = ccxt.binanceusdm({"enableRateLimit": True, "options": {"defaultType": "future"}})
        self.bybit = ccxt.bybit({"enableRateLimit": True, "options": {"defaultType": "linear"}})
        self._symbol_venue: dict[str, str] = {}  # BTCUSDT → binance|bybit
        self._markets_loaded = False

    def _load_markets(self) -> None:
        if self._markets_loaded:
            return
        self.binance.load_markets()
        try:
            self.bybit.load_markets()
        except Exception:
            pass
        self._markets_loaded = True

    def resolve(self, symbol: str) -> tuple[Any, str, str]:
        """Trả (exchange, ccxt_symbol, venue_name)."""
        self._load_markets()
        sym = symbol.upper().replace(".P", "")
        if sym in self._symbol_venue:
            venue = self._symbol_venue[sym]
            ex = self.binance if venue == "binance" else self.bybit
            return ex, self._ccxt_symbol(ex, sym), venue

        # Binance USDM: BTC/USDT:USDT
        b_sym = f"{sym[:-4]}/USDT:USDT" if sym.endswith("USDT") else sym
        if b_sym in self.binance.markets or sym in getattr(self.binance, "markets_by_id", {}):
            if b_sym in self.binance.markets:
                self._symbol_venue[sym] = "binance"
                return self.binance, b_sym, "binance"

        # thử id kiểu BTCUSDT
        for m, meta in self.binance.markets.items():
            if meta.get("swap") and meta.get("linear") and meta.get("base") and (meta.get("base") + "USDT") == sym:
                self._symbol_venue[sym] = "binance"
                return self.binance, m, "binance"

        # Bybit linear
        for m, meta in self.bybit.markets.items():
            if not meta.get("swap"):
                continue
            if (meta.get("base") or "") + "USDT" == sym or m.startswith(sym.replace("USDT", "") + "/USDT"):
                self._symbol_venue[sym] = "bybit"
                return self.bybit, m, "bybit"

        raise ValueError(f"Không tìm thấy perp {sym} trên Binance/Bybit.")

    def _ccxt_symbol(self, ex: Any, sym: str) -> str:
        if ex == self.binance:
            cand = f"{sym[:-4]}/USDT:USDT"
            if cand in ex.markets:
                return cand
        for m, meta in ex.markets.items():
            if meta.get("swap") and (meta.get("base") or "") + "USDT" == sym:
                return m
        raise ValueError(sym)

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        ex, ccxt_sym, _ = self.resolve(symbol)
        tf = TF_MAP[timeframe.upper()]
        rows = ex.fetch_ohlcv(ccxt_sym, timeframe=tf, limit=limit)
        df = pd.DataFrame(rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
        return df

    def fetch_last(self, symbol: str) -> float:
        ex, ccxt_sym, _ = self.resolve(symbol)
        t = ex.fetch_ticker(ccxt_sym)
        last = t.get("last") or t.get("close")
        if last is None:
            raise RuntimeError(f"Không lấy được giá {symbol}")
        return float(last)

    def venue_label(self, symbol: str) -> str:
        try:
            _, _, venue = self.resolve(symbol)
            return "Binance Perp" if venue == "binance" else "Bybit Perp"
        except Exception:
            return "Perp"

    def warmup(self, symbols: list[str]) -> None:
        self._load_markets()
        for s in symbols:
            try:
                self.resolve(s)
                time.sleep(0.05)
            except Exception as e:
                print(f"  ! Bỏ qua {s}: {e}")
