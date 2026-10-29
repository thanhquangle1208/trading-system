"""Lưu / đọc lịch sử noti."""

from __future__ import annotations

import time
from pathlib import Path

from sd_scanner.alert_history import AlertHistory, AlertRecord, telegram_message_link


def test_append_and_load_since(tmp_path: Path) -> None:
    path = tmp_path / "h.jsonl"
    h = AlertHistory(path)
    now = time.time()
    old = AlertRecord(
        ts=now - 48 * 3600,
        symbol="OLDUSDT",
        timeframe="H4",
        side="buy",
        price=1.0,
        zone_bot=0.9,
        zone_top=1.1,
        stl=0.975,
        tp=1.2,
        rr=2.0,
        depth=7.0,
        confidence=7.0,
    )
    new = AlertRecord(
        ts=now - 60,
        symbol="NEWUSDT",
        timeframe="D1",
        side="sell",
        price=2.0,
        zone_bot=1.9,
        zone_top=2.1,
        stl=2.05,
        tp=1.5,
        rr=3.0,
        depth=8.0,
        confidence=8.5,
        message_id=42,
        chat_id="-100999",
    )
    h.append(old)
    h.append(new)
    got = h.load_since(now - 24 * 3600)
    assert len(got) == 1
    assert got[0].symbol == "NEWUSDT"


def test_message_link_supergroup() -> None:
    link = telegram_message_link("-1001234567890", 77)
    assert link == "https://t.me/c/1234567890/77"


def test_message_link_private_none() -> None:
    assert telegram_message_link("123456789", 1) is None
