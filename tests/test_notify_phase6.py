"""Phase 6 — template Telegram + routing + dry-run send."""

from __future__ import annotations

from trading_system.notify.router import load_notify_config, resolve_channel
from trading_system.notify.telegram import TelegramNotifier
from trading_system.notify.templates import format_signal_message, format_test_message, rating_bar
from trading_system.settings import Settings
from trading_system.signals.models import SignalResult


def test_rating_bar() -> None:
    assert rating_bar(7) == "███████░░░"


def test_format_contains_required_fields() -> None:
    text = format_signal_message(
        channel_name="Tomas — tín hiệu chính",
        timeframe="H1",
        strategy_display_name="Confluence BTC Spot + Wyckoff",
        symbol="BTC/USDT",
        direction="long",
        score=72,
        rating=7,
        indicator_labels=["EMA 34/89", "Wyckoff cơ bản"],
    )
    assert "H1" in text
    assert "Confluence BTC Spot + Wyckoff" in text
    assert "Độ tin cậy: 7/10" in text
    assert "EMA 34/89" in text
    assert "Tomas — tín hiệu chính" in text


def test_resolve_default_channel() -> None:
    cfg = load_notify_config()
    ch = resolve_channel(cfg, timeframe="H1", strategy_id="btc_confluence_wyckoff")
    assert ch is not None
    assert ch.id == "main"


def test_send_test_dry_run_without_credentials() -> None:
    settings = Settings(telegram_bot_token="", telegram_chat_id="")
    n = TelegramNotifier(settings=settings)
    assert n.configured is False
    assert n.send_test(dry_run=True) is False


def test_send_signal_uses_injectable_send_fn() -> None:
    sent: list[tuple[str, str, str]] = []

    def fake_send(token: str, chat_id: str, text: str):
        sent.append((token, chat_id, text))
        return {"ok": True}

    settings = Settings(telegram_bot_token="tok", telegram_chat_id="123")
    n = TelegramNotifier(settings=settings, send_fn=fake_send)
    signal = SignalResult(
        strategy_id="btc_confluence_wyckoff",
        display_name="Confluence BTC Spot + Wyckoff",
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
    assert n.send_signal(signal, ["EMA 34/89"], dry_run=False) is True
    assert len(sent) == 1
    assert sent[0][0] == "tok"
    assert "Độ tin cậy: 8/10" in sent[0][2]
    assert format_test_message()
