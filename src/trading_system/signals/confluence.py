"""Engine confluence: AND required + score ≥ threshold + rating."""

from __future__ import annotations

from typing import Sequence

from trading_system.data.base import Candle
from trading_system.indicators.base import IndicatorResult
from trading_system.indicators.registry import get_indicator
from trading_system.logging_setup import get_logger
from trading_system.signals.conditions import evaluate_condition
from trading_system.signals.models import SignalResult, StrategySpec
from trading_system.signals.rating import confidence_rating

log = get_logger("signals.confluence")


def run_indicators(
    candles: Sequence[Candle],
    indicator_ids: list[str],
) -> dict[str, IndicatorResult]:
    out: dict[str, IndicatorResult] = {}
    for ind_id in indicator_ids:
        out[ind_id] = get_indicator(ind_id).compute(candles)
    return out


def evaluate_strategy(
    strategy: StrategySpec,
    candles: Sequence[Candle],
    timeframe: str,
) -> SignalResult:
    """Đánh giá 1 strategy trên 1 timeframe."""
    results = run_indicators(candles, strategy.indicator_ids)

    req_evals = [evaluate_condition(c, results) for c in strategy.required]
    opt_evals = [evaluate_condition(c, results) for c in strategy.optional]
    all_evals = req_evals + opt_evals

    required_ok = all(e.passed for e in req_evals) if req_evals else True
    # Điểm từ optional (và required nếu YAML gán points)
    score = sum(e.points_awarded for e in all_evals)
    # Không vượt score_max
    score = min(score, strategy.score_max)

    fired = required_ok and score >= strategy.score_threshold
    rating = confidence_rating(score, strategy.score_max, fired=fired)

    if not required_ok:
        reason = "thiếu điều kiện bắt buộc (AND)"
    elif score < strategy.score_threshold:
        reason = f"score {score:.0f} < ngưỡng {strategy.score_threshold:.0f}"
    else:
        reason = "đủ AND + score ≥ ngưỡng"

    snapshot = {
        i: {"values": r.values, "signals": r.signals} for i, r in results.items()
    }

    signal = SignalResult(
        strategy_id=strategy.id,
        display_name=strategy.display_name,
        symbol=strategy.symbol,
        timeframe=timeframe,
        direction=strategy.direction if fired else None,
        fired=fired,
        score=score,
        score_threshold=strategy.score_threshold,
        rating=rating,
        required_ok=required_ok,
        evaluations=all_evals,
        indicator_snapshot=snapshot,
        reason=reason,
    )
    log_fn = log.info if fired else log.debug
    log_fn(
        "Strategy %s TF=%s fired=%s score=%.0f rating=%s (%s)",
        strategy.id,
        timeframe,
        fired,
        score,
        rating,
        reason,
    )
    return signal


def evaluate_strategy_multi_tf(
    strategy: StrategySpec,
    candles_by_tf: dict[str, Sequence[Candle]],
) -> list[SignalResult]:
    """Chạy lần lượt các TF trong strategy (watchlist multi-TF)."""
    out: list[SignalResult] = []
    for tf in strategy.timeframes:
        if tf not in candles_by_tf:
            log.warning("Thiếu nến timeframe %s — bỏ qua", tf)
            continue
        out.append(evaluate_strategy(strategy, candles_by_tf[tf], tf))
    return out
