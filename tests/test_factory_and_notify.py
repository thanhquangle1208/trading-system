from __future__ import annotations

from trading_system.data.factory import get_exchange_adapter
from trading_system.data.mock import MockExchangeAdapter
from trading_system.notify.telegram import TelegramNotifier
from trading_system.settings import Settings


def test_factory_returns_mock_when_flag_true() -> None:
    settings = Settings(mock_exchange=True)
    adapter = get_exchange_adapter(settings)
    assert isinstance(adapter, MockExchangeAdapter)


def test_telegram_without_credentials_dry_run() -> None:
    settings = Settings(telegram_bot_token="", telegram_chat_id="")
    notifier = TelegramNotifier(settings)
    assert notifier.configured is False
    assert notifier.send_test() is False


def test_telegram_with_credentials_can_dry_run_or_fake_send() -> None:
    settings = Settings(telegram_bot_token="x", telegram_chat_id="1")
    notifier = TelegramNotifier(settings)
    assert notifier.configured is True
    # dry_run không gọi mạng
    assert notifier.send_test(dry_run=True) is False

    def fake(token, chat_id, text):
        return {"ok": True}

    n2 = TelegramNotifier(settings=settings, send_fn=fake)
    assert n2.send_test(dry_run=False) is True
