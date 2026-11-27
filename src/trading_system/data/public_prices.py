"""Giá hiện tại và nến ngày đã đóng. Không cần API key sàn.

Thứ tự: sàn ghi trong Notion (nếu đọc được) → Bybit → Binance → OKX → CoinGecko.
Nến ngày của sàn tập trung đóng lúc 00:00 UTC (07:00 giờ Việt Nam).
CoinGecko không có nến ngày thật: lấy giá đóng của nến 4 giờ cuối trong ngày UTC đã khép.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from urllib.parse import quote

from trading_system.data.http_client import HttpStatusError
from trading_system.logging_setup import get_logger
from trading_system.zones.reference import PriceTarget

log = get_logger("data.public_prices")

DAY_MS = 86_400_000
FOUR_H_MS = 4 * 60 * 60 * 1000


@dataclass(frozen=True)
class DailyCandle:
    open_ms: int
    close: float


@dataclass(frozen=True)
class Quote:
    price: float
    daily_close: float | None
    source: str


@dataclass
class FetchResult:
    quotes: dict[PriceTarget, Quote]
    id_cache: dict[str, str]
    unpriced: list[str]
    outage: bool


def latest_closed_daily(candles: list[DailyCandle], now: datetime) -> DailyCandle | None:
    """Nến ngày đã khép: thời điểm mở + 1 ngày <= now. Đúng mốc 00:00 UTC thì nến hôm trước đã đóng."""
    now_ms = _now_ms(now)
    closed = [c for c in candles if c.open_ms + DAY_MS <= now_ms]
    if not closed:
        return None
    return max(closed, key=lambda c: c.open_ms)


def parse_ohlc_rows(rows: list, now: datetime) -> float | None:
    """Hàng [open_ms, open, high, low, close, ...] — Binance, Bybit, OKX cùng dạng này."""
    candles: list[DailyCandle] = []
    for row in rows or []:
        if not isinstance(row, (list, tuple)) or len(row) < 5:
            continue
        try:
            candles.append(DailyCandle(open_ms=int(row[0]), close=float(row[4])))
        except (TypeError, ValueError):
            continue
    closed = latest_closed_daily(candles, now)
    return None if closed is None else closed.close


def coingecko_previous_day_close(rows: list, now: datetime) -> float | None:
    """Đóng của ngày UTC vừa khép, ghép từ nến 4 giờ (endpoint OHLC days=7)."""
    now_utc = _as_utc(now)
    midnight = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    day_start = midnight - timedelta(days=1)
    start_ms = int(day_start.timestamp() * 1000)
    end_ms = int(midnight.timestamp() * 1000)
    now_ms = int(now_utc.timestamp() * 1000)
    in_day: list[list] = []
    for row in rows or []:
        if not isinstance(row, (list, tuple)) or len(row) < 5:
            continue
        try:
            open_ms = int(row[0])
        except (TypeError, ValueError):
            continue
        if start_ms <= open_ms < end_ms and open_ms + FOUR_H_MS <= now_ms:
            in_day.append(list(row))
    if not in_day:
        return None
    last = max(in_day, key=lambda r: int(r[0]))
    try:
        return float(last[4])
    except (TypeError, ValueError):
        return None


def pick_coingecko_id(payload: dict, ticker: str) -> str | None:
    """Coin có symbol trùng khớp, ưu tiên hạng vốn hóa tốt hơn (số nhỏ hơn)."""
    want = ticker.lower()
    matches: list[tuple[int, str]] = []
    for coin in payload.get("coins") or []:
        if not isinstance(coin, dict):
            continue
        if str(coin.get("symbol") or "").lower() != want:
            continue
        cid = coin.get("id")
        if not cid:
            continue
        rank = coin.get("market_cap_rank")
        if isinstance(rank, int):
            rank_n = rank
        else:
            rank_n = 10**9
        matches.append((rank_n, str(cid)))
    if not matches:
        return None
    matches.sort()
    return matches[0][1]


class MarketBooks:
    """Cache một lần mỗi nguồn trong một lần chạy."""

    def __init__(self, http: Any, now: datetime, coingecko_key: str = "") -> None:
        self.http = http
        self.now = now
        self.coingecko_key = coingecko_key.strip()
        self._prices: dict[str, dict[str, float] | None] = {}
        self._daily: dict[tuple[str, str, str], float | None] = {}
        self.status: dict[str, str] = {}

    def price(self, venue: str, market: str, symbol: str) -> float | None:
        book = self._book(venue, market)
        if not book:
            return None
        return book.get(symbol)

    def daily(self, venue: str, market: str, symbol: str) -> float | None:
        key = (venue, market, symbol)
        if key not in self._daily:
            self._daily[key] = self._load_daily(venue, market, symbol)
        return self._daily[key]

    def cex_all_down(self) -> bool:
        if not self.status:
            return False
        return all(value == "error" for value in self.status.values())

    def _book(self, venue: str, market: str) -> dict[str, float] | None:
        key = f"{venue}-{market}"
        if key not in self._prices:
            self._prices[key] = self._load_book(venue, market)
        return self._prices[key]

    def _load_book(self, venue: str, market: str) -> dict[str, float] | None:
        key = f"{venue}-{market}"
        try:
            if venue == "binance":
                book = self._binance_book(market)
            elif venue == "bybit":
                book = self._bybit_book(market)
            elif venue == "okx":
                book = self._okx_book(market)
            else:
                book = None
        except HttpStatusError as exc:
            log.warning("Nguồn %s %s lỗi: %s", venue, market, exc)
            self.status[key] = "error"
            return None
        self.status[key] = "ok" if book is not None else "error"
        return book

    def _binance_book(self, market: str) -> dict[str, float] | None:
        if market == "perp":
            url = "https://fapi.binance.com/fapi/v1/ticker/price"
        else:
            url = "https://api.binance.com/api/v3/ticker/price"
        data = self.http.request_json("GET", url)
        if not isinstance(data, list):
            log.warning("Binance %s không trả danh sách giá", market)
            return None
        out: dict[str, float] = {}
        for row in data:
            if isinstance(row, dict) and row.get("symbol") and row.get("price") is not None:
                try:
                    out[str(row["symbol"])] = float(row["price"])
                except (TypeError, ValueError):
                    continue
        return out

    def _bybit_book(self, market: str) -> dict[str, float] | None:
        category = "linear" if market == "perp" else "spot"
        url = f"https://api.bybit.com/v5/market/tickers?category={category}"
        data = self.http.request_json("GET", url)
        if not isinstance(data, dict) or data.get("retCode") not in (0, None):
            log.warning("Bybit %s từ chối: %s", market, _short(data))
            return None
        rows = (data.get("result") or {}).get("list")
        if not isinstance(rows, list):
            log.warning("Bybit %s không có danh sách giá", market)
            return None
        out: dict[str, float] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            symbol = row.get("symbol")
            last = row.get("lastPrice")
            if symbol and last is not None:
                try:
                    out[str(symbol)] = float(last)
                except (TypeError, ValueError):
                    continue
        return out

    def _okx_book(self, market: str) -> dict[str, float] | None:
        inst_type = "SWAP" if market == "perp" else "SPOT"
        url = f"https://www.okx.com/api/v5/market/tickers?instType={inst_type}"
        data = self.http.request_json("GET", url)
        if not isinstance(data, dict) or str(data.get("code")) != "0":
            log.warning("OKX %s từ chối: %s", market, _short(data))
            return None
        rows = data.get("data")
        if not isinstance(rows, list):
            return None
        out: dict[str, float] = {}
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            inst = str(row.get("instId") or "")
            last = row.get("last")
            symbol = inst.replace("-SWAP", "").replace("-", "")
            if symbol and last is not None:
                try:
                    out[symbol] = float(last)
                except (TypeError, ValueError):
                    continue
        return out

    def _load_daily(self, venue: str, market: str, symbol: str) -> float | None:
        try:
            if venue == "binance":
                host = "https://fapi.binance.com/fapi/v1" if market == "perp" else "https://api.binance.com/api/v3"
                url = f"{host}/klines?symbol={symbol}&interval=1d&limit=3"
                data = self.http.request_json("GET", url)
                if not isinstance(data, list):
                    return None
                return parse_ohlc_rows(data, self.now)
            if venue == "bybit":
                category = "linear" if market == "perp" else "spot"
                url = (
                    "https://api.bybit.com/v5/market/kline"
                    f"?category={category}&symbol={symbol}&interval=D&limit=3"
                )
                data = self.http.request_json("GET", url)
                rows = ((data or {}).get("result") or {}).get("list") if isinstance(data, dict) else None
                return parse_ohlc_rows(rows or [], self.now)
            if venue == "okx":
                inst = _okx_inst(symbol, market)
                url = f"https://www.okx.com/api/v5/market/candles?instId={inst}&bar=1Dutc&limit=3"
                data = self.http.request_json("GET", url)
                rows = data.get("data") if isinstance(data, dict) else None
                return parse_ohlc_rows(rows or [], self.now)
        except HttpStatusError as exc:
            log.warning("Nến ngày %s %s %s lỗi: %s", venue, market, symbol, exc)
        return None


def fetch_quotes(
    http: Any,
    targets: list[PriceTarget],
    now: datetime,
    *,
    need_daily: set[PriceTarget],
    coingecko_key: str = "",
    id_cache: dict[str, str] | None = None,
    sleep: Callable[[float], None] | None = None,
) -> FetchResult:
    unique = list(dict.fromkeys(targets))
    books = MarketBooks(http, now, coingecko_key)
    quotes: dict[PriceTarget, Quote] = {}
    remaining: list[PriceTarget] = []
    for target in unique:
        quote = _cex_quote(books, target, need_daily)
        if quote is None:
            remaining.append(target)
        else:
            quotes[target] = quote
            log.info("Giá %s = %s qua %s", target.ticker, quote.price, quote.source)

    cache = {k.upper(): v for k, v in (id_cache or {}).items()}
    cg_error = False
    if remaining:
        cg_quotes, cache, cg_error = _coingecko_quotes(
            http,
            remaining,
            now,
            need_daily=need_daily,
            api_key=coingecko_key,
            id_cache=cache,
            sleep=sleep or _noop,
        )
        quotes.update(cg_quotes)

    unpriced = [t.ticker or t.symbol or "?" for t in unique if t not in quotes]
    # Gộp ticker trùng
    seen: set[str] = set()
    uniq_unpriced: list[str] = []
    for name in unpriced:
        if name not in seen:
            seen.add(name)
            uniq_unpriced.append(name)
    tried_cex = bool(books.status)
    outage = bool(unique) and not quotes and books.cex_all_down() and (cg_error or not remaining)
    if outage and not tried_cex:
        outage = cg_error
    return FetchResult(quotes=quotes, id_cache=cache, unpriced=uniq_unpriced, outage=outage)


def _cex_quote(books: MarketBooks, target: PriceTarget, need_daily: set[PriceTarget]) -> Quote | None:
    if not target.symbol:
        return None
    want_daily = target in need_daily
    for venue, market in _venue_order(target):
        price = books.price(venue, market, target.symbol)
        if price is None:
            continue
        daily = books.daily(venue, market, target.symbol) if want_daily else None
        return Quote(price=price, daily_close=daily, source=f"{venue} {market} {target.symbol}")
    return None


def _venue_order(target: PriceTarget) -> list[tuple[str, str]]:
    primary: list[tuple[str, str]] = []
    if target.venue in {"binance", "bybit", "okx"}:
        primary.append((target.venue, target.market))
        if target.market == "perp":
            primary.append((target.venue, "spot"))
    rest = [("bybit", "spot"), ("binance", "spot"), ("okx", "spot")]
    ordered: list[tuple[str, str]] = []
    for item in primary + rest:
        if item not in ordered:
            ordered.append(item)
    return ordered


def _coingecko_quotes(
    http: Any,
    targets: list[PriceTarget],
    now: datetime,
    *,
    need_daily: set[PriceTarget],
    api_key: str,
    id_cache: dict[str, str],
    sleep: Callable[[float], None],
) -> tuple[dict[PriceTarget, Quote], dict[str, str], bool]:
    headers = {"x-cg-demo-api-key": api_key} if api_key else None
    resolved: dict[PriceTarget, str] = {}
    error = False
    for target in targets:
        ticker = target.ticker
        if not ticker:
            continue
        cached = id_cache.get(ticker)
        if cached:
            resolved[target] = cached
            continue
        sleep(0.4)
        url = f"https://api.coingecko.com/api/v3/search?query={quote(ticker)}"
        try:
            payload = http.request_json("GET", url, headers=headers)
        except HttpStatusError as exc:
            log.warning("CoinGecko search %s lỗi: %s", ticker, exc)
            error = True
            continue
        if not isinstance(payload, dict):
            error = True
            continue
        cid = pick_coingecko_id(payload, ticker)
        if not cid:
            log.info("CoinGecko không có symbol %s — bỏ qua", ticker)
            continue
        id_cache[ticker] = cid
        resolved[target] = cid

    if not resolved:
        return {}, id_cache, error

    ids = sorted(set(resolved.values()))
    prices: dict[str, float] = {}
    url = "https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=" + ",".join(
        quote(i, safe="") for i in ids
    )
    try:
        payload = http.request_json("GET", url, headers=headers)
    except HttpStatusError as exc:
        log.warning("CoinGecko simple price lỗi: %s", exc)
        return {}, id_cache, True
    if isinstance(payload, dict):
        for cid, row in payload.items():
            if isinstance(row, dict) and row.get("usd") is not None:
                try:
                    prices[str(cid)] = float(row["usd"])
                except (TypeError, ValueError):
                    continue

    quotes: dict[PriceTarget, Quote] = {}
    for target, cid in resolved.items():
        price = prices.get(cid)
        if price is None:
            id_cache.pop(target.ticker, None)
            continue
        daily = None
        if target in need_daily:
            sleep(0.3)
            ohlc_url = (
                f"https://api.coingecko.com/api/v3/coins/{quote(cid, safe='')}"
                "/ohlc?vs_currency=usd&days=7"
            )
            try:
                rows = http.request_json("GET", ohlc_url, headers=headers)
                if isinstance(rows, list):
                    daily = coingecko_previous_day_close(rows, now)
            except HttpStatusError as exc:
                log.warning("CoinGecko OHLC %s lỗi: %s", cid, exc)
        quotes[target] = Quote(price=price, daily_close=daily, source=f"coingecko {cid}")
        log.info("Giá %s = %s qua coingecko %s", target.ticker, price, cid)
    return quotes, id_cache, error and not quotes


def _okx_inst(symbol: str, market: str) -> str:
    for quote_ccy in ("USDT", "USDC", "BUSD", "USD"):
        if symbol.endswith(quote_ccy) and len(symbol) > len(quote_ccy):
            inst = f"{symbol[: -len(quote_ccy)]}-{quote_ccy}"
            if market == "perp":
                inst += "-SWAP"
            return inst
    return symbol


def _now_ms(now: datetime) -> int:
    return int(_as_utc(now).timestamp() * 1000)


def _as_utc(now: datetime) -> datetime:
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def _short(data: object) -> str:
    text = str(data)
    return text[:180]


def _noop(_seconds: float) -> None:
    return None
