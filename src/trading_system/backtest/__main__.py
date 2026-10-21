"""Chạy: python -m trading_system.backtest"""

from __future__ import annotations

import json

from trading_system.backtest.config import load_backtest_config
from trading_system.backtest.costs import CostModel
from trading_system.backtest.engine import BacktestEngine
from trading_system.backtest.optimize import optimize_score_threshold
from trading_system.backtest.walk_forward import run_walk_forward, split_candles
from trading_system.data.base import Candle
from trading_system.data.factory import get_exchange_adapter
from trading_system.logging_setup import get_logger, setup_logging
from trading_system.settings import get_settings
from trading_system.signals.strategy_loader import load_strategy


def _synth_trend_candles(n: int = 260) -> list[Candle]:
    """Nến tổng hợp: sideway rồi uptrend — dùng khi mock quá nhiễu."""
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


def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    log = get_logger("backtest.main")
    cfg = load_backtest_config()

    # Ưu tiên mock/synth ổn định cho smoke (không phụ thuộc mạng)
    if settings.mock_exchange:
        candles = _synth_trend_candles(400)
        log.info("Dùng nến tổng hợp %d bars (MOCK)", len(candles))
    else:
        adapter = get_exchange_adapter(settings)
        candles = adapter.fetch_ohlcv("BTC/USDT", "H1", limit=300)
        adapter.close()
        log.info("Dùng nến exchange %d bars", len(candles))

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
        timeframe="H1",
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

    # Áp threshold tốt nhất lên full walk-forward
    from dataclasses import replace

    best_strategy = replace(engine.strategy, score_threshold=opt["best_score_threshold"])
    best_engine = BacktestEngine(
        strategy=best_strategy,
        costs=costs,
        initial_balance=cfg.initial_balance_usdt,
        warmup_bars=cfg.warmup_bars,
        timeframe="H1",
    )
    wf = run_walk_forward(candles, best_engine, cfg.train_ratio)
    report = {
        "optuna": {
            "best_score_threshold": opt["best_score_threshold"],
            "best_return_pct_train": opt["best_return_pct"],
        },
        "train": wf["train"].metrics.as_dict(),
        "test": wf["test"].metrics.as_dict(),
    }
    log.info("Báo cáo: %s", json.dumps(report, ensure_ascii=False, indent=2))
    log.info("Phase 5 backtest smoke xong.")


if __name__ == "__main__":
    main()
