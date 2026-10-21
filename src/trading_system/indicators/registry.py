"""Đăng ký & lấy plugin theo id — không hard-code tên trong logic nghiệp vụ khác."""

from __future__ import annotations

from trading_system.indicators.atr import Atr
from trading_system.indicators.base import IndicatorPlugin
from trading_system.indicators.bollinger import BollingerBands
from trading_system.indicators.candles_patterns import CandlePatterns
from trading_system.indicators.ema import Ema3489
from trading_system.indicators.macd import Macd
from trading_system.indicators.market_structure import MarketStructure
from trading_system.indicators.rsi import Rsi
from trading_system.indicators.support_resistance import SupportResistance
from trading_system.indicators.volume import VolumeStats
from trading_system.indicators.vwap import Vwap
from trading_system.indicators.wyckoff import WyckoffBasic

_REGISTRY: dict[str, type[IndicatorPlugin]] = {
    Ema3489.id: Ema3489,
    Rsi.id: Rsi,
    Macd.id: Macd,
    BollingerBands.id: BollingerBands,
    Vwap.id: Vwap,
    Atr.id: Atr,
    VolumeStats.id: VolumeStats,
    MarketStructure.id: MarketStructure,
    SupportResistance.id: SupportResistance,
    CandlePatterns.id: CandlePatterns,
    WyckoffBasic.id: WyckoffBasic,
}


def list_indicators() -> list[str]:
    return sorted(_REGISTRY.keys())


def get_indicator(indicator_id: str) -> IndicatorPlugin:
    cls = _REGISTRY.get(indicator_id)
    if cls is None:
        known = ", ".join(list_indicators())
        raise KeyError(f"Không có chỉ báo {indicator_id!r}. Có: {known}")
    return cls()


def compute_all(candles, ids: list[str] | None = None) -> dict[str, object]:
    """Chạy nhiều chỉ báo; bỏ qua cái thiếu nến (ghi lỗi trong values)."""
    selected = ids or list_indicators()
    out: dict[str, object] = {}
    for i in selected:
        plugin = get_indicator(i)
        try:
            out[i] = plugin.compute(candles)
        except ValueError as exc:
            out[i] = {"error": str(exc), "indicator_id": i}
    return out
