"""Chạy: python -m trading_system.backtest"""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone

from trading_system.backtest.config import load_backtest_config
from trading_system.backtest.costs import CostModel
from trading_system.backtest.engine import BacktestEngine
from trading_system.backtest.optimize import optimize_score_threshold
from trading_system.backtest.walk_forward import run_walk_forward, split_candles
from trading_system.data.base import Candle
from trading_system.data.ohlcv_history import fetch_real_btc_ohlcv
from trading_system.logging_setup import get_logger, setup_logging
from trading_system.settings import get_settings
from trading_system.signals.strategy_loader import load_strategy


def _synth_trend_candles(n: int = 260) -> list[Candle]:
    out: list[Candle] = []
    price = 100.0
    for i in range(n):
        if i < 120:
            price += (1 if i % 2 == 0 else -1) * 0.2
        else:
            price += 0.6
        out.append(
            Candle(
                timestamp_ms=1_700_000_000_000 + i * 3_600_000,
                open=price - 0.2,
                high=price + 1.2,
                low=price - 1.2,
                close=price,
                volume=120.0,
            )
        )
    return out


def _fmt_ts(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    log = get_logger("backtest.main")
    cfg = load_backtest_config()

    source = "mock"
    if cfg.data_mode == "real":
        candles, source = fetch_real_btc_ohlcv(
            symbol=cfg.symbol,
            timeframe=cfg.timeframe,
            limit_bars=cfg.bars,
            prefer=cfg.prefer_exchange,
        )
        log.info(
            "Nến thật %s %s từ %s: %d bars (%s → %s)",
            cfg.symbol,
            cfg.timeframe,
            source,
            len(candles),
            _fmt_ts(candles[0].timestamp_ms),
            _fmt_ts(candles[-1].timestamp_ms),
        )
        if source != cfg.prefer_exchange:
            log.warning(
                "Ưu tiên %s nhưng không truy cập được từ môi trường này "
                "(thường do chặn quốc gia). Đã dùng %s — giá BTC spot công khai.",
                cfg.prefer_exchange,
                source,
            )
    else:
        candles = _synth_trend_candles(400)
        log.info("Dùng nến tổng hợp %d bars (MOCK)", len(candles))

    costs = CostModel(
        fee_bps=cfg.fee_bps,
        slippage_bps=cfg.slippage_bps,
        funding_bps_per_bar=cfg.funding_bps_per_bar,
    )
    engine = BacktestEngine(
        strategy=load_strategy("btc_confluence_wyckoff.yaml"),
        costs=costs,
        initial_balance=cfg.initial_balance_usdt,
        warmup_bars=cfg.warmup_bars,
        timeframe=cfg.timeframe,
    )

    train, test = split_candles(candles, cfg.train_ratio)
    log.info("Walk-forward train=%d test=%d", len(train), len(test))

    opt = optimize_score_threshold(
        train,
        engine,
        n_trials=min(cfg.optuna_n_trials, 6),
        threshold_min=cfg.score_threshold_min,
        threshold_max=cfg.score_threshold_max,
    )
    log.info(
        "Optuna best threshold=%.1f return_train=%.2f%%",
        opt["best_score_threshold"],
        opt["best_return_pct"],
    )

    best_strategy = replace(engine.strategy, score_threshold=opt["best_score_threshold"])
    best_engine = BacktestEngine(
        strategy=best_strategy,
        costs=costs,
        initial_balance=cfg.initial_balance_usdt,
        warmup_bars=cfg.warmup_bars,
        timeframe=cfg.timeframe,
    )
    wf = run_walk_forward(candles, best_engine, cfg.train_ratio)
    report = {
        "data": {
            "mode": cfg.data_mode,
            "source_exchange": source,
            "prefer_exchange": cfg.prefer_exchange,
            "symbol": cfg.symbol,
            "timeframe": cfg.timeframe,
            "bars": len(candles),
            "from": _fmt_ts(candles[0].timestamp_ms),
            "to": _fmt_ts(candles[-1].timestamp_ms),
        },
        "optuna": {
            "best_score_threshold": opt["best_score_threshold"],
            "best_return_pct_train": opt["best_return_pct"],
        },
        "train": wf["train"].metrics.as_dict(),
        "test": wf["test"].metrics.as_dict(),
    }
    log.info("Báo cáo: %s", json.dumps(report, ensure_ascii=False, indent=2))
    log.info("Backtest data thật xong.")


if __name__ == "__main__":
    main()
