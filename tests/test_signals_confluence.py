"""Phase 3 — confluence AND + score + rating trên dữ liệu cố định."""

from __future__ import annotations

import json
from pathlib import Path

from trading_system.data.base import Candle
from trading_system.signals.confluence import evaluate_strategy
from trading_system.signals.rating import confidence_rating
from trading_system.signals.strategy_loader import load_strategy
from trading_system.storage.db import Database


def _uptrend_candles(n: int = 120) -> list[Candle]:
    """Chuỗi tăng rõ — EMA bullish, thường đủ điểm optional."""
    out: list[Candle] = []
    for i in range(n):
        c = 100.0 + i * 0.8
        out.append(
            Candle(
                timestamp_ms=1_700_000_000_000 + i * 3_600_000,
                open=c - 0.3,
                high=c + 1.0,
                low=c - 1.0,
                close=c,
                volume=100.0 + (50 if i == n - 1 else 0),
            )
        )
    return out


def _downtrend_candles(n: int = 120) -> list[Candle]:
    out: list[Candle] = []
    for i in range(n):
        c = 200.0 - i * 0.8
        out.append(
            Candle(
                timestamp_ms=1_700_000_000_000 + i * 3_600_000,
                open=c + 0.3,
                high=c + 1.0,
                low=c - 1.0,
                close=c,
                volume=100.0,
            )
        )
    return out


def test_load_wyckoff_strategy() -> None:
    s = load_strategy("btc_confluence_wyckoff.yaml")
    assert s.id == "btc_confluence_wyckoff"
    assert s.score_threshold == 60
    assert s.enabled is True
    assert any(c.indicator == "wyckoff_basic" for c in s.optional)


def test_rating_only_when_fired() -> None:
    assert confidence_rating(80, fired=False) is None
    r = confidence_rating(80, fired=True)
    assert r == 8
    assert confidence_rating(60, fired=True) == 6
    assert confidence_rating(100, fired=True) == 10


def test_uptrend_can_fire_signal() -> None:
    strategy = load_strategy("btc_confluence_wyckoff.yaml")
    result = evaluate_strategy(strategy, _uptrend_candles(), "H1")
    # Uptrend: EMA + market structure uptrend (required)
    assert result.required_ok is True
    assert result.fired is True
    assert result.rating is not None
    assert 1 <= result.rating <= 10
    assert result.direction == "long"
    assert result.score >= 60


def test_downtrend_fails_required_ema() -> None:
    strategy = load_strategy("btc_confluence_wyckoff.yaml")
    result = evaluate_strategy(strategy, _downtrend_candles(), "H1")
    assert result.required_ok is False
    assert result.fired is False
    assert result.rating is None
    assert "bắt buộc" in result.reason


def test_minimal_strategy_score_gate() -> None:
    """example: required 30 + optional — cần ≥60 để fire."""
    strategy = load_strategy("example_confluence.yaml")
    up = evaluate_strategy(strategy, _uptrend_candles(), "H1")
    # required OK trên uptrend; fired phụ thuộc optional đủ điểm
    assert up.required_ok is True
    down = evaluate_strategy(strategy, _downtrend_candles(), "H1")
    assert down.fired is False


def test_save_signal_to_db(tmp_path: Path) -> None:
    db = Database(tmp_path / "sig.db")
    db.init_schema()
    strategy = load_strategy("btc_confluence_wyckoff.yaml")
    result = evaluate_strategy(strategy, _uptrend_candles(), "H1")
    sid = db.insert_signal(
        symbol=result.symbol,
        timeframe=result.timeframe,
        direction=result.direction,
        score=result.score,
        rating=result.rating,
        strategy_id=result.strategy_id,
        payload_json=json.dumps(result.as_dict(), ensure_ascii=False),
    )
    assert sid > 0
    row = db.connection.execute("SELECT * FROM signals WHERE id = ?", (sid,)).fetchone()
    assert row["strategy_id"] == "btc_confluence_wyckoff"
    db.close()
