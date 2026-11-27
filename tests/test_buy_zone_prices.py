"""Giá công khai: nến ngày 00:00 UTC, sàn trong ghi chú, CoinGecko khi không có cặp."""

from __future__ import annotations

from datetime import datetime, timezone

from trading_system.data.http_client import HttpStatusError
from trading_system.data.public_prices import (
    coingecko_previous_day_close,
    fetch_quotes,
    latest_closed_daily,
    parse_ohlc_rows,
    pick_coingecko_id,
    DailyCandle,
)
from trading_system.zones.reference import parse_reference
from tests.fakes import FakeHttp


def _ms(year, month, day, hour=0) -> int:
    return int(datetime(year, month, day, hour, tzinfo=timezone.utc).timestamp() * 1000)


def test_reference_picks_binance_spot_symbol() -> None:
    target = parse_reference("Spot / Binance BTCUSDT", "btc")
    assert target.venue == "binance"
    assert target.symbol == "BTCUSDT"
    assert target.market == "spot"
    assert target.ticker == "BTC"

    perp = parse_reference("Bybit perp ETH/USDT", "ETH")
    assert perp.venue == "bybit"
    assert perp.symbol == "ETHUSDT"
    assert perp.market == "perp"

    default = parse_reference("", "hype")
    assert default.venue is None
    assert default.symbol == "HYPEUSDT"


def test_daily_candle_closes_at_utc_midnight() -> None:
    prev = _ms(2026, 11, 26)
    cur = _ms(2026, 11, 27)
    rows = [
        [prev, "1", "1", "1", "52700", "0"],
        [cur, "1", "1", "1", "99999", "0"],
    ]
    before = datetime(2026, 11, 26, 23, 59, tzinfo=timezone.utc)
    assert parse_ohlc_rows(rows, before) is None

    at_close = datetime(2026, 11, 27, 0, 0, tzinfo=timezone.utc)
    assert parse_ohlc_rows(rows, at_close) == 52700

    # Bybit trả nến mới nhất trước — vẫn lấy nến đã đóng, không lấy nến đang chạy
    newest_first = list(reversed(rows))
    assert parse_ohlc_rows(newest_first, datetime(2026, 11, 27, 0, 5, tzinfo=timezone.utc)) == 52700

    closed = latest_closed_daily(
        [DailyCandle(prev, 52700), DailyCandle(cur, 99999)],
        at_close,
    )
    assert closed is not None and closed.close == 52700


def test_coingecko_uses_previous_utc_day_and_exact_symbol() -> None:
    rows = []
    for hour in (0, 4, 8, 12, 16, 20):
        rows.append([_ms(2026, 11, 26, hour), 1, 1, 1, 100 + hour])
    rows.append([_ms(2026, 11, 27, 0), 1, 1, 1, 999])
    now = datetime(2026, 11, 27, 0, 30, tzinfo=timezone.utc)
    assert coingecko_previous_day_close(rows, now) == 120

    midday = datetime(2026, 11, 26, 23, 0, tzinfo=timezone.utc)
    assert coingecko_previous_day_close(rows, midday) is None

    chosen = pick_coingecko_id(
        {
            "coins": [
                {"id": "fake-hype", "symbol": "HYPE", "market_cap_rank": 400},
                {"id": "hyperliquid", "symbol": "hype", "market_cap_rank": 12},
                {"id": "sec-coin", "symbol": "sec", "market_cap_rank": 1},
            ]
        },
        "HYPE",
    )
    assert chosen == "hyperliquid"
    assert pick_coingecko_id({"coins": [{"id": "x", "symbol": "btc"}]}, "SECZ") is None


def test_binance_reference_is_used_and_blocked_venue_falls_back() -> None:
    now = datetime(2026, 11, 27, 1, 0, tzinfo=timezone.utc)
    target = parse_reference("Spot / Binance BTCUSDT", "BTC")
    http = FakeHttp(
        [
            (
                "GET",
                "api.binance.com/api/v3/ticker/price",
                [{"symbol": "BTCUSDT", "price": "60850"}],
            ),
            (
                "GET",
                "api.bybit.com",
                [{"symbol": "BTCUSDT", "lastPrice": "1"}],
            ),
        ]
    )
    # Bybit handler above won't match because method path is tickers dict, not a list.
    # Binance succeeds first, so Bybit must not be required.
    result = fetch_quotes(http, [target], now, need_daily=set(), sleep=lambda _s: None)
    assert result.quotes[target].price == 60850
    assert result.quotes[target].source.startswith("binance")
    assert result.outage is False
    assert not any("bybit" in call["url"] for call in http.calls)

    blocked = FakeHttp(
        [
            ("GET", "api.binance.com", HttpStatusError(451, "binance", "restricted")),
            (
                "GET",
                "api.bybit.com/v5/market/tickers",
                {"retCode": 0, "result": {"list": [{"symbol": "BTCUSDT", "lastPrice": "60000"}]}},
            ),
        ]
    )
    result = fetch_quotes(blocked, [target], now, need_daily=set(), sleep=lambda _s: None)
    assert result.quotes[target].price == 60000
    assert "bybit" in result.quotes[target].source


def test_unlisted_token_uses_coingecko_and_unknown_symbol_is_unpriced() -> None:
    now = datetime(2026, 11, 27, 1, 0, tzinfo=timezone.utc)
    hype = parse_reference("", "HYPE")
    secz = parse_reference("", "SECZ")

    def search(_method, url, _body):
        if "query=HYPE" in url:
            return {"coins": [{"id": "hyperliquid", "symbol": "hype", "market_cap_rank": 12}]}
        return {"coins": [{"id": "bitcoin", "symbol": "btc", "market_cap_rank": 1}]}

    http = FakeHttp(
        [
            ("GET", "api.binance.com", HttpStatusError(451, "binance", "restricted")),
            ("GET", "api.bybit.com", HttpStatusError(451, "bybit", "restricted")),
            ("GET", "okx.com", HttpStatusError(451, "okx", "restricted")),
            ("GET", "api.coingecko.com/api/v3/search", search),
            (
                "GET",
                "api.coingecko.com/api/v3/simple/price",
                {"hyperliquid": {"usd": 25.5}},
            ),
        ]
    )
    result = fetch_quotes(
        http,
        [hype, secz],
        now,
        need_daily=set(),
        sleep=lambda _s: None,
    )
    assert result.outage is False
    assert result.quotes[hype].price == 25.5
    assert result.quotes[hype].source == "coingecko hyperliquid"
    assert secz not in result.quotes
    assert "SECZ" in result.unpriced
    assert result.id_cache["HYPE"] == "hyperliquid"
    assert "SECZ" not in result.id_cache
