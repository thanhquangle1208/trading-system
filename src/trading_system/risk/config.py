"""Đọc configs/risk.yaml thành object dễ dùng."""

from __future__ import annotations

from dataclasses import dataclass

from trading_system.config_loader import load_risk


@dataclass(frozen=True)
class RiskConfig:
    risk_per_trade_pct: float
    atr_period: int
    atr_stop_mult: float
    atr_tp1_mult: float
    atr_tp2_mult: float
    partial_tp_pct: float
    hold_losers_auto: bool
    hold_losers_manual_only: bool
    perp_require_stop_loss: bool
    max_leverage: float
    kill_switch: bool
    max_open_orders: int
    max_daily_loss_pct: float


def load_risk_config() -> RiskConfig:
    raw = load_risk()
    sizing = raw.get("sizing") or {}
    spot = raw.get("spot") or {}
    perp = raw.get("perp") or {}
    return RiskConfig(
        risk_per_trade_pct=float(raw.get("risk_per_trade_pct", 1.0)),
        atr_period=int(sizing.get("atr_period", 14)),
        atr_stop_mult=float(sizing.get("atr_stop_mult", 1.5)),
        atr_tp1_mult=float(sizing.get("atr_tp1_mult", 2.0)),
        atr_tp2_mult=float(sizing.get("atr_tp2_mult", 3.5)),
        partial_tp_pct=float(sizing.get("partial_tp_pct", 0.5)),
        hold_losers_auto=bool(spot.get("hold_losers_auto", False)),
        hold_losers_manual_only=bool(spot.get("hold_losers_manual_only", True)),
        perp_require_stop_loss=bool(perp.get("require_stop_loss", True)),
        max_leverage=float(perp.get("max_leverage", 10)),
        kill_switch=bool(raw.get("kill_switch", False)),
        max_open_orders=int(raw.get("max_open_orders", 5)),
        max_daily_loss_pct=float(raw.get("max_daily_loss_pct", 3.0)),
    )
