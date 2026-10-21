"""Đọc số liệu từ SQLite cho dashboard."""

from __future__ import annotations

from typing import Any

from trading_system.settings import get_settings
from trading_system.storage.db import Database


def load_dashboard_snapshot(db: Database | None = None) -> dict[str, Any]:
    own = db is None
    db = db or Database.from_settings(get_settings())
    if own:
        db.init_schema()

    balance = None
    account_id = None
    try:
        row = db.connection.execute(
            "SELECT id, balance, name FROM paper_accounts ORDER BY id LIMIT 1"
        ).fetchone()
        if row:
            account_id = int(row["id"])
            balance = float(row["balance"])
    except Exception:
        balance = None

    orders = []
    if account_id is not None:
        orders = [
            dict(r)
            for r in db.connection.execute(
                """
                SELECT id, symbol, side, quantity, price, status, rating,
                       stop_loss, take_profit_1, take_profit_2, created_at
                FROM paper_orders WHERE account_id = ?
                ORDER BY id DESC LIMIT 20
                """,
                (account_id,),
            ).fetchall()
        ]

    signals = [
        dict(r)
        for r in db.connection.execute(
            """
            SELECT id, symbol, timeframe, direction, score, rating, strategy_id, created_at
            FROM signals ORDER BY id DESC LIMIT 20
            """
        ).fetchall()
    ]

    n_orders = len(orders)
    rated = [o["rating"] for o in orders if o.get("rating") is not None]
    avg_rating = sum(rated) / len(rated) if rated else None

    if own:
        db.close()

    return {
        "balance": balance,
        "orders": orders,
        "signals": signals,
        "n_orders": n_orders,
        "n_signals": len(signals),
        "avg_rating": avg_rating,
    }
