from __future__ import annotations

from trading_system.data.factory import get_exchange_adapter
from trading_system.data.mock import MockExchangeAdapter
from trading_system.notify.telegram_skeleton import TelegramNotifierSkeleton
from trading_system.settings import Settings


def test_factory_returns_mock_when_flag_true() -> None:
    settings = Settings(mock_exchange=True)
    adapter = get_exchange_adapter(settings)
    assert isinstance(adapter, MockExchangeAdapter)


def test_telegram_skeleton_without_credentials() -> None:
    settings = Settings(telegram_bot_token="", telegram_chat_id="")
    notifier = TelegramNotifierSkeleton(settings)
    assert notifier.configured is False
    assert notifier.send_test() is False


def test_telegram_skeleton_with_credentials() -> None:
    settings = Settings(telegram_bot_token="x", telegram_chat_id="1")
    notifier = TelegramNotifierSkeleton(settings)
    assert notifier.configured is True
    assert notifier.send_test("hi") is True
