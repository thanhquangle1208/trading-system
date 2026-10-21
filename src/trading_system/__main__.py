"""Chạy smoke Phase 1–3: mock feed + chỉ báo + confluence/rating + paper."""

from __future__ import annotations

import json

from trading_system.config_loader import load_risk, load_watchlist
from trading_system.data.factory import get_exchange_adapter
from trading_system.execution.paper import PaperBroker
from trading_system.indicators.registry import list_indicators
from trading_system.logging_setup import get_logger, setup_logging
from trading_system.notify.telegram_skeleton import TelegramNotifierSkeleton
from trading_system.settings import get_settings
from trading_system.signals.confluence import evaluate_strategy
from trading_system.signals.strategy_loader import load_strategy
from trading_system.storage.db import Database


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    log = get_logger("main")

    log.info("Trading System Phase 1–3 smoke — env=%s tz=%s", settings.app_env, settings.timezone)

    watchlist = load_watchlist()
    risk = load_risk()
    symbol = (watchlist.get("symbols") or ["BTC/USDT"])[0]
    timeframe = (watchlist.get("timeframes") or ["H1"])[0]
    score_threshold = (risk.get("confluence") or {}).get("score_threshold", 60)
    log.info("Watchlist %s TF=%s | confluence threshold=%s", symbol, timeframe, score_threshold)
    log.info("Chỉ báo: %s", ", ".join(list_indicators()))

    db = Database.from_settings(settings)
    db.init_schema()
    account_id = db.ensure_paper_account(
        "default",
        balance=settings.paper_starting_balance_usdt,
    )

    adapter = get_exchange_adapter(settings)
    candles = adapter.fetch_ohlcv(symbol, timeframe, limit=120)
    price = adapter.fetch_ticker_price(symbol)
    saved = db.save_candles(adapter.name, symbol, timeframe, candles)
    log.info("Giá %s ≈ %.2f | đã lưu %d nến (%s)", symbol, price, saved, adapter.name)

    strategy = load_strategy("btc_confluence_wyckoff.yaml")
    signal = evaluate_strategy(strategy, candles, timeframe)
    log.info(
        "Tín hiệu %s: fired=%s score=%.0f rating=%s — %s",
        signal.display_name,
        signal.fired,
        signal.score,
        signal.rating,
        signal.reason,
    )
    if signal.fired:
        sid = db.insert_signal(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            direction=signal.direction,
            score=signal.score,
            rating=signal.rating,
            strategy_id=signal.strategy_id,
            payload_json=json.dumps(signal.as_dict(), ensure_ascii=False),
        )
        log.info("Đã lưu signal id=%s (Độ tin cậy=%s/10)", sid, signal.rating)

    broker = PaperBroker(db, account_id)
    qty = 0.001
    fill = broker.market_order(
        symbol,
        "buy",
        quantity=qty,
        price=price,
        rating=signal.rating if signal.fired else None,
    )
    log.info("Paper fill order_id=%s balance_after=%.2f", fill.order_id, fill.balance_after)

    TelegramNotifierSkeleton(settings).send_test()
    adapter.close()
    db.close()
    log.info("Phase 1–3 smoke xong.")


if __name__ == "__main__":
    main()
