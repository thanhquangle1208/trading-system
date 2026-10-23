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
        self.binance_ok = False
        self.bybit_ok = False

    def _load_markets(self) -> None:
        if self._markets_loaded:
            return
        try:
            self.binance.load_markets()
            self.binance_ok = True
        except Exception as e:
            print(f"  ! Binance markets: {e}")
            self.binance_ok = False
        try:
            self.bybit.load_markets()
            self.bybit_ok = True
        except Exception as e:
            print(f"  ! Bybit markets: {e}")
            self.bybit_ok = False
        if not self.binance_ok and not self.bybit_ok:
            raise RuntimeError("Không tải được markets Binance lẫn Bybit.")
        self._markets_loaded = True

    def resolve(self, symbol: str) -> tuple[Any, str, str]:
        """Trả (exchange, ccxt_symbol, venue_name)."""
        self._load_markets()
        sym = symbol.upper().replace(".P", "")
        if sym in self._symbol_venue:
            venue = self._symbol_venue[sym]
            ex = self.binance if venue == "binance" else self.bybit
            return ex, self._ccxt_symbol(ex, sym), venue

        if self.binance_ok:
            b_sym = f"{sym[:-4]}/USDT:USDT" if sym.endswith("USDT") else sym
            if b_sym in self.binance.markets:
                self._symbol_venue[sym] = "binance"
                return self.binance, b_sym, "binance"
            for m, meta in self.binance.markets.items():
                if meta.get("swap") and meta.get("base") and (meta.get("base") + "USDT") == sym:
                    self._symbol_venue[sym] = "binance"
                    return self.binance, m, "binance"

        if self.bybit_ok:
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

    def search_perp_tickers(self, query: str, limit: int = 10) -> list[dict[str, str]]:
        """
        Tìm perp USDT. Ưu tiên Binance; không có kết quả mới sang Bybit.
        Trả list dict: symbol (BTCUSDT), venue, label (hiển thị).
        """
        self._load_markets()
        q = query.strip().upper().replace(".P", "").replace("/", "").replace("-", "").replace(" ", "")
        if not q:
            return []
        if q.endswith("USDT"):
            base_q = q[:-4]
            full_q = q
        else:
            base_q = q
            full_q = q + "USDT"

        def collect(ex: Any, venue: str) -> list[dict[str, str]]:
            exact: list[dict[str, str]] = []
            prefix: list[dict[str, str]] = []
            fuzzy: list[dict[str, str]] = []
            for _m, meta in ex.markets.items():
                if meta.get("active") is False:
                    continue
                if meta.get("option"):
                    continue
                if not meta.get("swap", False) and meta.get("type") not in ("swap", "future"):
                    continue
                quote = (meta.get("quote") or "").upper()
                settle = (meta.get("settle") or "").upper()
                base = (meta.get("base") or "").upper()
                market_id = (meta.get("id") or "").upper().replace("_", "").replace("-", "")
                if quote != "USDT" and settle != "USDT" and not market_id.endswith("USDT"):
                    continue
                if not base:
                    continue
                store = base + "USDT"
                # 1000PEPE… giữ base gốc
                if market_id.endswith("USDT") and len(market_id) > 4:
                    store = market_id

                b = base
                mid = market_id
                hit_exact = b == base_q or store == full_q or mid == full_q
                hit_prefix = b.startswith(base_q) or mid.startswith(base_q)
                hit_fuzzy = base_q in b or base_q in mid
                if not (hit_exact or hit_prefix or hit_fuzzy):
                    continue

                row = {
                    "symbol": store,
                    "venue": venue,
                    "label": f"{store} · {venue}",
                }
                if hit_exact:
                    exact.append(row)
                elif hit_prefix:
                    prefix.append(row)
                else:
                    fuzzy.append(row)

            seen: set[str] = set()
            out: list[dict[str, str]] = []
            for row in exact + prefix + fuzzy:
                if row["symbol"] in seen:
                    continue
                seen.add(row["symbol"])
                out.append(row)
                if len(out) >= limit:
                    break
            return out

        if self.binance_ok:
            found = collect(self.binance, "Binance Perp")
            if found:
                return found
        if self.bybit_ok:
            return collect(self.bybit, "Bybit Perp")
        return []
