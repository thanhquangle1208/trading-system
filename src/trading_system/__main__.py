"""Chạy smoke Phase 1+2: logging + DB + mock feed + paper + vài chỉ báo."""

from __future__ import annotations

from trading_system.config_loader import load_risk, load_watchlist
from trading_system.data.factory import get_exchange_adapter
from trading_system.execution.paper import PaperBroker
from trading_system.indicators.registry import get_indicator, list_indicators
from trading_system.logging_setup import get_logger, setup_logging
from trading_system.notify.telegram_skeleton import TelegramNotifierSkeleton
from trading_system.settings import get_settings
from trading_system.storage.db import Database


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    log = get_logger("main")

    log.info("Trading System Phase 1+2 smoke — env=%s tz=%s", settings.app_env, settings.timezone)

    watchlist = load_watchlist()
    risk = load_risk()
    symbol = (watchlist.get("symbols") or ["BTC/USDT"])[0]
    timeframe = (watchlist.get("timeframes") or ["H1"])[0]
    score_threshold = (risk.get("confluence") or {}).get("score_threshold", 60)
    log.info("Watchlist %s TF=%s | confluence threshold=%s", symbol, timeframe, score_threshold)

    db = Database.from_settings(settings)
    db.init_schema()
    account_id = db.ensure_paper_account(
        "default",
        balance=settings.paper_starting_balance_usdt,
    )

    adapter = get_exchange_adapter(settings)
    # Đủ nến cho EMA 89 / MACD
    candles = adapter.fetch_ohlcv(symbol, timeframe, limit=120)
    price = adapter.fetch_ticker_price(symbol)
    saved = db.save_candles(adapter.name, symbol, timeframe, candles)
    log.info("Giá %s ≈ %.2f | đã lưu %d nến (%s)", symbol, price, saved, adapter.name)

    log.info("Chỉ báo có sẵn: %s", ", ".join(list_indicators()))
    for ind_id in ("ema_34_89", "rsi", "wyckoff_basic"):
        result = get_indicator(ind_id).compute(candles)
        log.info(
            "  %s → values=%s signals=%s",
            result.display_name,
            {k: result.values.get(k) for k in list(result.values)[:4]},
            result.signals,
        )

    broker = PaperBroker(db, account_id)
    qty = 0.001
    fill = broker.market_order(symbol, "buy", quantity=qty, price=price, rating=None)
    log.info("Paper fill order_id=%s balance_after=%.2f", fill.order_id, fill.balance_after)

    TelegramNotifierSkeleton(settings).send_test()
    adapter.close()
    db.close()
    log.info("Phase 1+2 smoke xong.")


if __name__ == "__main__":
    main()
