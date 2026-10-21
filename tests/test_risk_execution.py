"""Phase 4 — sizing, SL/TP, guards, paper execute."""

from __future__ import annotations

from pathlib import Path

import pytest

from trading_system.data.base import Candle
from trading_system.execution.paper import LiveBrokerStub, PaperBroker
from trading_system.risk.config import RiskConfig, load_risk_config
from trading_system.risk.engine import RiskEngine
from trading_system.risk.sizing import position_size_from_atr
from trading_system.risk.stops import compute_stop_levels
from trading_system.signals.confluence import evaluate_strategy
from trading_system.signals.models import SignalResult
from trading_system.signals.strategy_loader import load_strategy
from trading_system.storage.db import Database


def _fired_signal() -> SignalResult:
    return SignalResult(
        strategy_id="test",
        display_name="Test",
        symbol="BTC/USDT",
        timeframe="H1",
        direction="long",
        fired=True,
        score=80,
        score_threshold=60,
        rating=8,
        required_ok=True,
        evaluations=[],
        reason="test",
    )


def _cfg(**overrides) -> RiskConfig:
    base = load_risk_config()
    data = base.__dict__.copy()
    data.update(overrides)
    return RiskConfig(**data)


def test_atr_sizing_math() -> None:
    qty, risk, dist = position_size_from_atr(
        balance=1000,
        risk_per_trade_pct=1.0,
        atr=100,
        atr_stop_mult=1.5,
    )
    assert risk == pytest.approx(10.0)
    assert dist == pytest.approx(150.0)
    assert qty == pytest.approx(10 / 150)


def test_stop_levels_long() -> None:
    levels = compute_stop_levels(
        entry=100,
        side="buy",
        atr=2,
        atr_stop_mult=1.5,
        atr_tp1_mult=2.0,
        atr_tp2_mult=3.5,
    )
    assert levels.stop_loss == pytest.approx(97.0)
    assert levels.take_profit_1 == pytest.approx(104.0)
    assert levels.take_profit_2 == pytest.approx(107.0)


def test_kill_switch_rejects() -> None:
    engine = RiskEngine(_cfg(kill_switch=True))
    plan = engine.plan_order(
        signal=_fired_signal(),
        entry_price=50_000,
        atr=500,
        balance=1000,
    )
    assert plan.approved is False
    assert "kill_switch" in (plan.reject_reason or "")


def test_max_open_orders_rejects() -> None:
    engine = RiskEngine(_cfg(max_open_orders=2))
    plan = engine.plan_order(
        signal=_fired_signal(),
        entry_price=50_000,
        atr=500,
        balance=1000,
        open_orders=2,
    )
    assert plan.approved is False
    assert "max_open_orders" in (plan.reject_reason or "")


def test_perp_missing_sl_rejects() -> None:
    engine = RiskEngine(_cfg(perp_require_stop_loss=True))
    plan = engine.plan_order(
        signal=_fired_signal(),
        entry_price=50_000,
        atr=500,
        balance=1000,
        market_type="perp",
        force_omit_stop=True,
    )
    assert plan.approved is False
    assert "Stop Loss" in (plan.reject_reason or "")


def test_spot_plan_approved_and_paper_fill(tmp_path: Path) -> None:
    engine = RiskEngine(_cfg(kill_switch=False))
    plan = engine.plan_order(
        signal=_fired_signal(),
        entry_price=50_000,
        atr=500,
        balance=1000,
        market_type="spot",
    )
    assert plan.approved is True
    assert plan.stop_loss is not None
    assert plan.take_profit_1 is not None
    assert plan.rating == 8

    db = Database(tmp_path / "p4.db")
    db.init_schema()
    account_id = db.ensure_paper_account("default", 1000.0)
    fill = PaperBroker(db, account_id).execute_plan(plan)
    assert fill.order_id > 0
    assert fill.stop_loss == plan.stop_loss
    assert fill.rating == 8
    row = db.connection.execute(
        "SELECT stop_loss, rating FROM paper_orders WHERE id = ?",
        (fill.order_id,),
    ).fetchone()
    assert row["rating"] == 8
    assert row["stop_loss"] == pytest.approx(plan.stop_loss)
    db.close()


def test_rejected_plan_cannot_execute(tmp_path: Path) -> None:
    engine = RiskEngine(_cfg(kill_switch=True))
    plan = engine.plan_order(
        signal=_fired_signal(),
        entry_price=50_000,
        atr=500,
        balance=1000,
    )
    db = Database(tmp_path / "rej.db")
    db.init_schema()
    account_id = db.ensure_paper_account("default", 1000.0)
    with pytest.raises(ValueError, match="từ chối"):
        PaperBroker(db, account_id).execute_plan(plan)
    db.close()


def test_live_stub_not_implemented() -> None:
    plan = RiskEngine().plan_order(
        signal=_fired_signal(),
        entry_price=50_000,
        atr=500,
        balance=1000,
    )
    with pytest.raises(NotImplementedError):
        LiveBrokerStub().execute_plan(plan)


def test_daily_loss_guard() -> None:
    engine = RiskEngine(_cfg(max_daily_loss_pct=3.0))
    plan = engine.plan_order(
        signal=_fired_signal(),
        entry_price=50_000,
        atr=500,
        balance=960,  # lỗ 4% từ 1000
        starting_balance=1000,
    )
    assert plan.approved is False
    assert "lỗ trong ngày" in (plan.reject_reason or "")


def test_integration_uptrend_signal_to_plan() -> None:
    strategy = load_strategy("btc_confluence_wyckoff.yaml")
    candles = []
    for i in range(120):
        c = 100.0 + i * 0.8
        candles.append(
            Candle(
                timestamp_ms=1_700_000_000_000 + i * 3_600_000,
                open=c - 0.3,
                high=c + 1.0,
                low=c - 1.0,
                close=c,
                volume=100.0,
            )
        )
    signal = evaluate_strategy(strategy, candles, "H1")
    assert signal.fired is True
    from trading_system.indicators.atr import Atr

    atr = Atr().compute(candles).values["atr"]
    plan = RiskEngine().plan_order(
        signal=signal,
        entry_price=candles[-1].close,
        atr=float(atr),
        balance=1000,
    )
    assert plan.approved is True
    assert plan.quantity > 0
