"""Phase 6 — dashboard API / HTML."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from trading_system.dashboard.app import app
from trading_system.dashboard.data import load_dashboard_snapshot
from trading_system.storage.db import Database


def test_snapshot_from_db(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "dash.db"
    db = Database(db_path)
    db.init_schema()
    aid = db.ensure_paper_account("default", 1000.0)
    db.insert_paper_order(
        aid, "BTC/USDT", "buy", 0.01, 50000, rating=8, stop_loss=49000, take_profit_1=51000
    )
    db.insert_signal(
        symbol="BTC/USDT",
        timeframe="H1",
        direction="long",
        score=75,
        rating=8,
        strategy_id="btc_confluence_wyckoff",
        payload_json="{}",
    )
    snap = load_dashboard_snapshot(db)
    assert snap["balance"] == 1000.0
    assert snap["n_orders"] == 1
    assert snap["n_signals"] == 1
    assert snap["avg_rating"] == 8
    db.close()


def test_dashboard_home_and_api() -> None:
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert "Trading System" in r.text
    assert "Độ tin cậy" in r.text

    api = client.get("/api/snapshot")
    assert api.status_code == 200
    body = api.json()
    assert "orders" in body
    assert "signals" in body
