"""Data feed + exchange adapters (CEX ccxt; DEX chỗ cắm sau)."""

from trading_system.data.base import Candle, ExchangeAdapter
from trading_system.data.factory import get_exchange_adapter

__all__ = ["Candle", "ExchangeAdapter", "get_exchange_adapter"]
