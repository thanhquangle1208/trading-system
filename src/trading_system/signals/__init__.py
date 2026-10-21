"""Phase 3 — confluence + rating Độ tin cậy."""

from trading_system.signals.confluence import evaluate_strategy, evaluate_strategy_multi_tf
from trading_system.signals.models import SignalResult, StrategySpec
from trading_system.signals.strategy_loader import load_strategy

__all__ = [
    "SignalResult",
    "StrategySpec",
    "evaluate_strategy",
    "evaluate_strategy_multi_tf",
    "load_strategy",
]
