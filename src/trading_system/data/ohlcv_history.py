"""Tải nến lịch sử công khai qua ccxt (paginate). Ưu tiên Bybit, fallback nếu bị chặn."""

from __future__ import annotations

import time
from typing import Any

import ccxt

from trading_system.data.base import Candle
from trading_system.data.timeframes import to_ccxt_timeframe
from trading_system.logging_setup import get_logger

log = get_logger("data.ohlcv_history")

# Thứ tự thử khi Bybit không vào được từ môi trường agent
_FALLBACK_EXCHANGES = ("okx", "gate", "kucoin", "kraken")


def _to_candles(raw: list[list]) -> list[Candle]:
    return [
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


def fetch_ohlcv_paginated(
    exchange: Any,
    symbol: str,
    timeframe: str,
    *,
    limit_bars: int = 500,
    page_size: int = 200,
) -> list[Candle]:
    """Lấy nhiều trang OHLCV từ quá khứ đến hiện tại."""
    tf = to_ccxt_timeframe(timeframe)
    ms_per_bar = int(exchange.parse_timeframe(tf) * 1000)
    # Bắt đầu từ quá khứ đủ xa
    since = exchange.milliseconds() - limit_bars * ms_per_bar
    all_rows: list[list] = []
    safety = 0
    while len(all_rows) < limit_bars and safety < 40:
        safety += 1
        batch = exchange.fetch_ohlcv(symbol, timeframe=tf, since=since, limit=page_size)
        if not batch:
            break
        all_rows.extend(batch)
        since = int(batch[-1][0]) + ms_per_bar
        if len(batch) < page_size:
            break
        time.sleep(exchange.rateLimit / 1000 if exchange.rateLimit else 0.05)

    # unique by timestamp, sort, cắt đuôi
    by_ts = {int(r[0]): r for r in all_rows}
    rows = [by_ts[k] for k in sorted(by_ts)]
    if len(rows) > limit_bars:
        rows = rows[-limit_bars:]
    return _to_candles(rows)


def fetch_real_btc_ohlcv(
    *,
    symbol: str = "BTC/USDT",
    timeframe: str = "H1",
    limit_bars: int = 500,
    prefer: str = "bybit",
) -> tuple[list[Candle], str]:
    """
    Trả (candles, exchange_id_đã_dùng).
    Thử Bybit trước; nếu 403/geo-block → OKX/Gate/…
    """
    order = [prefer] + [e for e in _FALLBACK_EXCHANGES if e != prefer]
    errors: list[str] = []

    for ex_id in order:
        try:
            klass = getattr(ccxt, ex_id)
            exchange = klass({"enableRateLimit": True, "options": {"defaultType": "spot"}})
            # Một số sàn cần load_markets; bắt lỗi sớm
            candles = fetch_ohlcv_paginated(
                exchange,
                symbol,
                timeframe,
                limit_bars=limit_bars,
            )
            close_fn = getattr(exchange, "close", None)
            if callable(close_fn):
                close_fn()
            if len(candles) < 120:
                errors.append(f"{ex_id}: chỉ {len(candles)} nến")
                continue
            log.info(
                "Đã tải %d nến %s %s từ %s (close cuối=%.2f)",
                len(candles),
                symbol,
                timeframe,
                ex_id,
                candles[-1].close,
            )
            return candles, ex_id
        except Exception as exc:  # noqa: BLE001 — thử sàn tiếp
            msg = f"{ex_id}: {type(exc).__name__}: {str(exc)[:160]}"
            errors.append(msg)
            log.warning("Không lấy được nến từ %s — %s", ex_id, msg)

    raise RuntimeError(
        "Không tải được nến thật từ bất kỳ sàn nào. Chi tiết:\n- " + "\n- ".join(errors)
    )
