from __future__ import annotations

from pathlib import Path

from trading_system.config_loader import load_exchanges, load_risk, load_watchlist
from trading_system.logging_setup import get_logger, setup_logging


def test_watchlist_has_btc_and_tfs() -> None:
    wl = load_watchlist()
    assert "BTC/USDT" in wl["symbols"]
    for tf in ("M15", "H1", "H4", "D1"):
        assert tf in wl["timeframes"]
    assert wl["timezone"] == "Asia/Ho_Chi_Minh"


def test_risk_confluence_threshold_60() -> None:
    risk = load_risk()
    assert risk["confluence"]["score_threshold"] == 60
    assert risk["rating"]["label"] == "Độ tin cậy"
    assert risk["starting_balance_usdt"] == 1000


def test_exchanges_bybit_spot_enabled() -> None:
    cfg = load_exchanges()
    bybit = cfg["exchanges"]["bybit"]
    assert bybit["enabled"] is True
    assert bybit["market_type"] == "spot"
    assert cfg["dex"]["enabled"] is False


def test_logging_writes_file(tmp_path: Path) -> None:
    setup_logging("INFO", log_dir=tmp_path)
    log = get_logger("test")
    log.info("xin chào phase 1")
    content = (tmp_path / "app.log").read_text(encoding="utf-8")
    assert "xin chào phase 1" in content
