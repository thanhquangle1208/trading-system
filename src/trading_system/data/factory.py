"""Chọn adapter theo settings / config — không hard-code tên sàn trong logic nghiệp vụ."""

from __future__ import annotations

from trading_system.config_loader import load_exchanges
from trading_system.data.base import ExchangeAdapter
from trading_system.data.bybit import BybitCcxtAdapter
from trading_system.data.dex_placeholder import DexAdapterPlaceholder
from trading_system.data.mock import MockExchangeAdapter
from trading_system.logging_setup import get_logger
from trading_system.settings import Settings, get_settings

log = get_logger("data.factory")


def get_exchange_adapter(settings: Settings | None = None) -> ExchangeAdapter:
    settings = settings or get_settings()

    if settings.mock_exchange:
        log.info("Dùng MockExchangeAdapter (MOCK_EXCHANGE=true)")
        return MockExchangeAdapter()

    exchanges_cfg = load_exchanges()
    default_id = settings.exchange_id or exchanges_cfg.get("default", "bybit")
    exch = (exchanges_cfg.get("exchanges") or {}).get(default_id, {})

    if not exch.get("enabled", True):
        raise RuntimeError(f"Exchange {default_id!r} đang enabled=false trong configs/exchanges.yaml")

    adapter_name = exch.get("adapter", "bybit_ccxt")
    testnet = bool(settings.exchange_testnet if settings.exchange_testnet is not None else exch.get("testnet", True))

    if adapter_name in ("bybit_ccxt", "bybit") or default_id == "bybit":
        return BybitCcxtAdapter(
            api_key=settings.bybit_api_key,
            api_secret=settings.bybit_api_secret,
            testnet=testnet,
        )

    if adapter_name in ("dex", "dex_placeholder") or default_id == "dex":
        return DexAdapterPlaceholder()

    raise ValueError(f"Adapter không hỗ trợ: {adapter_name!r} (exchange={default_id})")
