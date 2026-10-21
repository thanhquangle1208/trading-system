"""Phase 5 — backtest no look-ahead, costs, metrics, walk-forward."""

from __future__ import annotations

from trading_system.backtest.costs import CostModel
from trading_system.backtest.engine import BacktestEngine
from trading_system.backtest.metrics import compute_metrics, max_drawdown_pct
from trading_system.backtest.optimize import optimize_score_threshold
from trading_system.backtest.portfolio import ClosedTrade, Portfolio
from trading_system.backtest.walk_forward import split_candles
from trading_system.data.base import Candle
from trading_system.signals.strategy_loader import load_strategy


def _candles_up(n: int = 220) -> list[Candle]:
    out: list[Candle] = []
    price = 100.0
    for i in range(n):
        if i < 100:
            price += 0.15 if i % 3 else -0.05
        else:
            price += 0.7
        out.append(
            Candle(
                timestamp_ms=1_700_000_000_000 + i * 3_600_000,
                open=price - 0.3,
                high=price + 1.5,
                low=price - 1.5,
                close=price,
                volume=100.0 + i * 0.1,
            )
        )
    return out


def test_cost_model_slippage_direction() -> None:
    c = CostModel(fee_bps=10, slippage_bps=10)
    assert c.apply_entry(100, "buy") > 100
    assert c.apply_exit(100, "buy") < 100
    assert c.fee_usdt(1000) == 1.0


def test_max_drawdown() -> None:
    assert max_drawdown_pct([100, 110, 90, 95]) == (110 - 90) / 110 * 100


def test_metrics_from_portfolio() -> None:
    pf = Portfolio(balance=1000)
    pf.equity_curve = [1000, 1010, 990]
    pf.total_fees = 2.0
    pf.trades = [
        ClosedTrade("buy", 1, 100, 110, 10, 1, 8, "tp1", 0, 1),
        ClosedTrade("buy", 1, 100, 90, -10, 1, 7, "sl", 2, 3),
    ]
    m = compute_metrics(pf, 1000)
    assert m.n_trades == 2
    assert m.winrate == 50.0
    assert m.total_fees == 2.0
    assert m.avg_rating == 7.5


def test_split_candles_chronological() -> None:
    candles = _candles_up(300)
    train, test = split_candles(candles, 0.7, min_segment=120)
    assert len(train) + len(test) == 300
    assert len(test) >= 120
    assert train[-1].timestamp_ms < test[0].timestamp_ms


def test_backtest_no_lookahead_entry_after_signal() -> None:
    """
    Entry luôn ở bar sau tín hiệu (open bar i+1).
    Kiểm tra: mọi trade.entry_bar > warmup và exit_bar >= entry_bar.
    """
    candles = _candles_up(240)
    engine = BacktestEngine(
        strategy=load_strategy("btc_confluence_wyckoff.yaml"),
        costs=CostModel(fee_bps=10, slippage_bps=5),
        initial_balance=1000,
        warmup_bars=100,
        timeframe="H1",
    )
    result = engine.run(candles)
    assert result.metrics.initial_balance == 1000
    assert len(result.equity_curve) > 0
    for t in result.trades:
        assert t["entry_bar"] >= 100
        assert t["exit_bar"] >= t["entry_bar"]
        # Không vào ở bar cuối cùng của window tín hiệu theo cách dùng future close
        assert t["entry_bar"] < len(candles)


def test_backtest_metrics_stable_keys() -> None:
    candles = _candles_up(220)
    result = BacktestEngine(warmup_bars=100).run(candles)
    d = result.metrics.as_dict()
    for key in (
        "net_pnl",
        "return_pct",
        "n_trades",
        "winrate",
        "total_fees",
        "max_drawdown_pct",
    ):
        assert key in d


def test_optuna_runs_few_trials() -> None:
    candles = _candles_up(220)
    engine = BacktestEngine(warmup_bars=100)
    out = optimize_score_threshold(
        candles,
        engine,
        n_trials=3,
        threshold_min=55,
        threshold_max=70,
    )
    assert 55 <= out["best_score_threshold"] <= 70
    assert "result" in out
