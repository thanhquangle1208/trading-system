"""Optuna — tối ưu nhẹ score_threshold trên đoạn train."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Sequence

import optuna

from trading_system.backtest.engine import BacktestEngine, BacktestResult
from trading_system.data.base import Candle
from trading_system.logging_setup import get_logger
from trading_system.signals.models import StrategySpec

log = get_logger("backtest.optimize")

# Optuna log ồn — tắt mặc định
optuna.logging.set_verbosity(optuna.logging.WARNING)


def optimize_score_threshold(
    candles: Sequence[Candle],
    base_engine: BacktestEngine,
    *,
    n_trials: int = 8,
    threshold_min: float = 50,
    threshold_max: float = 80,
) -> dict[str, Any]:
    """
    Mục tiêu: maximize return_pct trên tập candles (thường là train).
    Trả best_threshold + best metrics.
    """

    def objective(trial: optuna.Trial) -> float:
        thr = trial.suggest_float("score_threshold", threshold_min, threshold_max)
        strategy = _with_threshold(base_engine.strategy, thr)
        engine = BacktestEngine(
            strategy=strategy,
            risk=base_engine.risk,
            costs=base_engine.costs,
            initial_balance=base_engine.initial_balance,
            warmup_bars=base_engine.warmup_bars,
            timeframe=base_engine.timeframe,
            market_type=base_engine.market_type,
        )
        result = engine.run(candles)
        trial.set_user_attr("metrics", result.metrics.as_dict())
        return result.metrics.return_pct

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=False)

    best_thr = float(study.best_params["score_threshold"])
    best_metrics = study.best_trial.user_attrs.get("metrics", {})
    log.info("Optuna best score_threshold=%.1f return=%.2f%%", best_thr, study.best_value)

    # Chạy lại với best để có BacktestResult đầy đủ
    strategy = _with_threshold(base_engine.strategy, best_thr)
    best_engine = BacktestEngine(
        strategy=strategy,
        risk=base_engine.risk,
        costs=base_engine.costs,
        initial_balance=base_engine.initial_balance,
        warmup_bars=base_engine.warmup_bars,
        timeframe=base_engine.timeframe,
        market_type=base_engine.market_type,
    )
    best_result: BacktestResult = best_engine.run(candles)
    return {
        "best_score_threshold": best_thr,
        "best_return_pct": study.best_value,
        "best_metrics": best_metrics,
        "result": best_result.as_dict(),
        "n_trials": n_trials,
    }


def _with_threshold(strategy: StrategySpec, threshold: float) -> StrategySpec:
    return replace(strategy, score_threshold=float(threshold))
