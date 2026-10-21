"""Walk-forward: chia train / test theo thời gian (không xáo trộn)."""

from __future__ import annotations

from typing import Sequence

from trading_system.backtest.engine import BacktestEngine, BacktestResult
from trading_system.data.base import Candle


def split_candles(
    candles: Sequence[Candle],
    train_ratio: float = 0.7,
    *,
    min_segment: int = 120,
) -> tuple[list[Candle], list[Candle]]:
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio phải trong (0, 1)")
    n = len(candles)
    if n < min_segment * 2:
        raise ValueError(
            f"Cần ≥ {min_segment * 2} nến để walk-forward, đang có {n}"
        )
    cut = int(n * train_ratio)
    # Đảm bảo test đủ dài (warmup + vài bar)
    if n - cut < min_segment:
        cut = n - min_segment
    if cut < min_segment:
        cut = min_segment
    return list(candles[:cut]), list(candles[cut:])


def _engine_for_segment(engine: BacktestEngine, n_bars: int) -> BacktestEngine:
    """
    Warmup tối thiểu ~89 (EMA chậm). Không hạ dưới mức chỉ báo cần.
    """
    min_for_indicators = 89
    warmup = min(engine.warmup_bars, n_bars - 5)
    warmup = max(min_for_indicators, warmup)
    if n_bars <= warmup + 2:
        raise ValueError(
            f"Đoạn {n_bars} nến quá ngắn (cần > {warmup + 2} với warmup={warmup})"
        )
    return BacktestEngine(
        strategy=engine.strategy,
        risk=engine.risk,
        costs=engine.costs,
        initial_balance=engine.initial_balance,
        warmup_bars=warmup,
        timeframe=engine.timeframe,
        market_type=engine.market_type,
    )


def run_walk_forward(
    candles: Sequence[Candle],
    engine: BacktestEngine,
    train_ratio: float = 0.7,
) -> dict[str, BacktestResult]:
    train, test = split_candles(candles, train_ratio, min_segment=120)
    return {
        "train": _engine_for_segment(engine, len(train)).run(train),
        "test": _engine_for_segment(engine, len(test)).run(test),
    }
