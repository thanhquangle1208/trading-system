"""Chặn lệnh nguy hiểm: kill switch, limits, perp bắt buộc SL."""

from __future__ import annotations

from trading_system.risk.config import RiskConfig


def check_kill_switch(cfg: RiskConfig) -> str | None:
    if cfg.kill_switch:
        return "kill_switch đang bật — dừng mọi lệnh mới"
    return None


def check_max_open_orders(cfg: RiskConfig, open_orders: int) -> str | None:
    if open_orders >= cfg.max_open_orders:
        return f"đã đủ max_open_orders={cfg.max_open_orders} (hiện {open_orders})"
    return None


def check_daily_loss(
    cfg: RiskConfig,
    *,
    starting_balance: float,
    current_balance: float,
) -> str | None:
    if starting_balance <= 0:
        return None
    loss_pct = (starting_balance - current_balance) / starting_balance * 100.0
    if loss_pct >= cfg.max_daily_loss_pct:
        return (
            f"lỗ trong ngày ~{loss_pct:.1f}% ≥ trần {cfg.max_daily_loss_pct}% "
            "(max_daily_loss_pct)"
        )
    return None


def check_perp_requires_sl(
    cfg: RiskConfig,
    *,
    market_type: str,
    stop_loss: float | None,
) -> str | None:
    if market_type.lower() == "perp" and cfg.perp_require_stop_loss:
        if stop_loss is None:
            return "perp bắt buộc Stop Loss — thiếu SL, từ chối lệnh"
    return None


def check_hold_losers_policy(
    cfg: RiskConfig,
    *,
    market_type: str,
    hold_losers_manual: bool,
) -> str | None:
    """
    Spot: không cho auto hold losers.
    Chỉ khi hold_losers_manual=True (bạn xác nhận tay) mới được phép flag.
    """
    if market_type.lower() != "spot":
        return None
    if cfg.hold_losers_auto:
        return "cấu hình hold_losers_auto=true không được phép — chỉ manual"
    if hold_losers_manual and not cfg.hold_losers_manual_only:
        return "hold losers manual bị tắt trong config"
    return None
