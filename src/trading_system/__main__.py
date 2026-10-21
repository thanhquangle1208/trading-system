"""Smoke Phase 1–4: mock → confluence → risk plan → paper (hoặc reject)."""

from __future__ import annotations

import json

from trading_system.config_loader import load_risk, load_watchlist
from trading_system.data.factory import get_exchange_adapter
from trading_system.execution.paper import PaperBroker
from trading_system.indicators.atr import Atr
from trading_system.indicators.registry import list_indicators
from trading_system.logging_setup import get_logger, setup_logging
from trading_system.notify.telegram_skeleton import TelegramNotifierSkeleton
from trading_system.risk.engine import RiskEngine
from trading_system.settings import get_settings
from trading_system.signals.confluence import evaluate_strategy
from trading_system.signals.strategy_loader import load_strategy
from trading_system.storage.db import Database


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    log = get_logger("main")

    log.info("Trading System Phase 1–4 smoke — env=%s tz=%s", settings.app_env, settings.timezone)

    watchlist = load_watchlist()
    risk_raw = load_risk()
    symbol = (watchlist.get("symbols") or ["BTC/USDT"])[0]
    timeframe = (watchlist.get("timeframes") or ["H1"])[0]
    log.info(
        "Watchlist %s TF=%s | kill_switch=%s | indicators=%s",
        symbol,
        timeframe,
        risk_raw.get("kill_switch"),
        ", ".join(list_indicators()),
    )

    db = Database.from_settings(settings)
    db.init_schema()
    account_id = db.ensure_paper_account(
        "default",
        balance=settings.paper_starting_balance_usdt,
    )
    balance = db.get_paper_balance(account_id)

    adapter = get_exchange_adapter(settings)
    candles = adapter.fetch_ohlcv(symbol, timeframe, limit=120)
    price = adapter.fetch_ticker_price(symbol)
    db.save_candles(adapter.name, symbol, timeframe, candles)

    strategy = load_strategy("btc_confluence_wyckoff.yaml")
    signal = evaluate_strategy(strategy, candles, timeframe)
    log.info(
        "Tín hiệu: fired=%s score=%.0f rating=%s — %s",
        signal.fired,
        signal.score,
        signal.rating,
        signal.reason,
    )
    if signal.fired:
        db.insert_signal(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            direction=signal.direction,
            score=signal.score,
            rating=signal.rating,
            strategy_id=signal.strategy_id,
            payload_json=json.dumps(signal.as_dict(), ensure_ascii=False),
        )

    atr = float(Atr().compute(candles).values["atr"] or 0)
    engine = RiskEngine()
    plan = engine.plan_order(
        signal=signal,
        entry_price=price,
        atr=atr if atr > 0 else price * 0.01,
        balance=balance,
        open_orders=db.count_paper_orders(account_id),
        starting_balance=settings.paper_starting_balance_usdt,
        market_type="spot",
    )
    log.info(
        "Risk plan: approved=%s qty=%.6f SL=%s TP1=%s reason=%s",
        plan.approved,
        plan.quantity,
        plan.stop_loss,
        plan.take_profit_1,
        plan.reject_reason,
    )

    if plan.approved:
        fill = PaperBroker(db, account_id).execute_plan(plan)
        log.info(
            "Paper fill order_id=%s balance_after=%.2f rating=%s",
            fill.order_id,
            fill.balance_after,
            fill.rating,
        )
    else:
        log.info("Không đặt paper — plan bị từ chối")

    TelegramNotifierSkeleton(settings).send_test()
    adapter.close()
    db.close()
    log.info("Phase 1–4 smoke xong.")


if __name__ == "__main__":
    main()
