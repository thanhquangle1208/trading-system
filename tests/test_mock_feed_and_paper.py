from __future__ import annotations

from pathlib import Path

import pytest

from trading_system.data.dex_placeholder import DexAdapterPlaceholder
from trading_system.data.mock import MockExchangeAdapter
from trading_system.data.timeframes import to_ccxt_timeframe
from trading_system.execution.paper import PaperBroker
from trading_system.storage.db import Database


def test_timeframe_mapping() -> None:
    assert to_ccxt_timeframe("M15") == "15m"
    assert to_ccxt_timeframe("H1") == "1h"
    assert to_ccxt_timeframe("H4") == "4h"
    assert to_ccxt_timeframe("D1") == "1d"
    with pytest.raises(ValueError):
        to_ccxt_timeframe("M5")


def test_mock_ohlcv_and_ticker() -> None:
    adapter = MockExchangeAdapter(base_price=61_000.0)
    candles = adapter.fetch_ohlcv("BTC/USDT", "H1", limit=10)
    assert len(candles) == 10
    assert candles[0].open > 0
    assert adapter.fetch_ticker_price("BTC/USDT") == 61_000.0


def test_dex_placeholder_not_implemented() -> None:
    dex = DexAdapterPlaceholder()
    with pytest.raises(NotImplementedError):
        dex.fetch_ticker_price("BTC/USDT")


def test_paper_buy_updates_balance(tmp_path: Path) -> None:
    db = Database(tmp_path / "paper.db")
    db.init_schema()
    account_id = db.ensure_paper_account("default", 1000.0)
    broker = PaperBroker(db, account_id)

    fill = broker.market_order("BTC/USDT", "buy", quantity=0.01, price=50_000.0)
    assert fill.order_id > 0
    # 0.01 * 50000 = 500
    assert fill.balance_after == pytest.approx(500.0)
    assert db.get_paper_balance(account_id) == pytest.approx(500.0)

    with pytest.raises(ValueError, match="Không đủ số dư"):
        broker.market_order("BTC/USDT", "buy", quantity=1.0, price=50_000.0)

    db.close()


def test_save_candles(tmp_path: Path) -> None:
    db = Database(tmp_path / "candles.db")
    db.init_schema()
    adapter = MockExchangeAdapter()
    candles = adapter.fetch_ohlcv("BTC/USDT", "M15", limit=3)
    n = db.save_candles("mock", "BTC/USDT", "M15", candles)
    assert n == 3
    cur = db.connection.execute("SELECT COUNT(*) AS c FROM candles")
    assert int(cur.fetchone()["c"]) == 3
    db.close()
