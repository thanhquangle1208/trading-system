"""Risk engine: từ tín hiệu + giá/ATR → OrderPlan (approve hoặc reject)."""

from __future__ import annotations

from trading_system.logging_setup import get_logger
from trading_system.risk.config import RiskConfig, load_risk_config
from trading_system.risk.guards import (
    check_daily_loss,
    check_hold_losers_policy,
    check_kill_switch,
    check_max_open_orders,
    check_perp_requires_sl,
)
from trading_system.risk.models import OrderPlan
from trading_system.risk.sizing import position_size_from_atr
from trading_system.risk.stops import compute_stop_levels
from trading_system.signals.models import SignalResult

log = get_logger("risk.engine")


class RiskEngine:
    def __init__(self, config: RiskConfig | None = None) -> None:
        self.config = config or load_risk_config()

    def plan_order(
        self,
        *,
        signal: SignalResult,
        entry_price: float,
        atr: float,
        balance: float,
        open_orders: int = 0,
        starting_balance: float | None = None,
        market_type: str = "spot",
        hold_losers_manual: bool = False,
        force_omit_stop: bool = False,
    ) -> OrderPlan:
        """
        force_omit_stop: chỉ dùng trong test — giả lập thiếu SL trên perp.
        """
        cfg = self.config
        starting = starting_balance if starting_balance is not None else balance
        side = "buy" if (signal.direction or "long") == "long" else "sell"

        def reject(reason: str) -> OrderPlan:
            log.info("OrderPlan REJECT: %s", reason)
            return OrderPlan(
                symbol=signal.symbol,
                side=side,
                quantity=0.0,
                entry_price=entry_price,
                stop_loss=None,
                take_profit_1=None,
                take_profit_2=None,
                partial_tp_pct=cfg.partial_tp_pct,
                market_type=market_type,
                rating=signal.rating,
                risk_usdt=0.0,
                atr=atr,
                approved=False,
                reject_reason=reason,
                hold_losers_allowed=False,
            )

        if not signal.fired:
            return reject("không có tín hiệu (signal.fired=false)")

        for checker in (
            check_kill_switch(cfg),
            check_max_open_orders(cfg, open_orders),
            check_daily_loss(cfg, starting_balance=starting, current_balance=balance),
            check_hold_losers_policy(
                cfg, market_type=market_type, hold_losers_manual=hold_losers_manual
            ),
        ):
            if checker:
                return reject(checker)

        try:
            qty, risk_usdt, _ = position_size_from_atr(
                balance=balance,
                risk_per_trade_pct=cfg.risk_per_trade_pct,
                atr=atr,
                atr_stop_mult=cfg.atr_stop_mult,
            )
            levels = compute_stop_levels(
                entry=entry_price,
                side=side,
                atr=atr,
                atr_stop_mult=cfg.atr_stop_mult,
                atr_tp1_mult=cfg.atr_tp1_mult,
                atr_tp2_mult=cfg.atr_tp2_mult,
            )
        except ValueError as exc:
            return reject(str(exc))

        stop_loss = None if force_omit_stop else levels.stop_loss
        perp_err = check_perp_requires_sl(
            cfg, market_type=market_type, stop_loss=stop_loss
        )
        if perp_err:
            return reject(perp_err)

        hold_ok = bool(hold_losers_manual and market_type.lower() == "spot")

        plan = OrderPlan(
            symbol=signal.symbol,
            side=side,
            quantity=qty,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit_1=levels.take_profit_1,
            take_profit_2=levels.take_profit_2,
            partial_tp_pct=cfg.partial_tp_pct,
            market_type=market_type,
            rating=signal.rating,
            risk_usdt=risk_usdt,
            atr=atr,
            approved=True,
            reject_reason=None,
            hold_losers_allowed=hold_ok,
        )
        log.info(
            "OrderPlan OK %s %s qty=%.6f SL=%s TP1=%s rating=%s",
            plan.side,
            plan.symbol,
            plan.quantity,
            plan.stop_loss,
            plan.take_profit_1,
            plan.rating,
        )
        return plan
