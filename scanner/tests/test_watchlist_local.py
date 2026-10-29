"""watchlist.local.yaml — cặp không nằm file Git."""

from __future__ import annotations

from pathlib import Path

from sd_scanner.watchlist_store import ensure_local_symbols, load_raw, save_symbols


def test_creates_local_from_seed(tmp_path: Path) -> None:
    path, syms = ensure_local_symbols(tmp_path, ["BTCUSDT", "ETHUSDT"])
    assert path.name == "watchlist.local.yaml"
    assert path.is_file()
    assert syms == ["BTCUSDT", "ETHUSDT"]
    assert load_raw(path)["symbols"] == ["BTCUSDT", "ETHUSDT"]


def test_prefers_existing_local(tmp_path: Path) -> None:
    local = tmp_path / "watchlist.local.yaml"
    save_symbols(local, ["SOLUSDT", "LINKUSDT"])
    path, syms = ensure_local_symbols(tmp_path, ["BTCUSDT"])
    assert path == local
    assert syms == ["SOLUSDT", "LINKUSDT"]
