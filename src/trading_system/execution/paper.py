"""Paper broker — thực thi OrderPlan đã được risk duyệt."""

from __future__ import annotations

from dataclasses import dataclass

from trading_system.logging_setup import get_logger
from trading_system.risk.models import OrderPlan
from trading_system.storage.db import Database

log = get_logger("execution.paper")


@dataclass
class PaperFill:
    order_id: int
    symbol: str
    side: str
    quantity: float
    price: float
    balance_after: float
    stop_loss: float | None = None
    take_profit_1: float | None = None
    take_profit_2: float | None = None
    rating: int | None = None


class PaperBroker:
    """Giả lập spot: trừ/cộng USDT theo giá × số lượng."""

    def __init__(self, db: Database, account_id: int) -> None:
        self.db = db
        self.account_id = account_id

    def execute_plan(self, plan: OrderPlan) -> PaperFill:
        if not plan.approved:
            raise ValueError(
                f"Không thực thi plan bị từ chối: {plan.reject_reason or 'unknown'}"
            )
        return self.market_order(
            symbol=plan.symbol,
            side=plan.side,
            quantity=plan.quantity,
            price=plan.entry_price,
            rating=plan.rating,
            stop_loss=plan.stop_loss,
            take_profit_1=plan.take_profit_1,
            take_profit_2=plan.take_profit_2,
            market_type=plan.market_type,
        )

    def market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        rating: int | None = None,
        stop_loss: float | None = None,
        take_profit_1: float | None = None,
        take_profit_2: float | None = None,
        market_type: str = "spot",
    ) -> PaperFill:
        side_n = side.lower().strip()
        if side_n not in ("buy", "sell"):
            raise ValueError("side phải là buy hoặc sell")
        if quantity <= 0 or price <= 0:
            raise ValueError("quantity và price phải > 0")

        balance = self.db.get_paper_balance(self.account_id)
        notional = quantity * price

        if side_n == "buy":
            if notional > balance:
                raise ValueError(
                    f"Không đủ số dư paper: cần {notional:.2f}, còn {balance:.2f} USDT"
                )
            new_balance = balance - notional
        else:
            new_balance = balance + notional

        self.db.connection.execute(
            "UPDATE paper_accounts SET balance = ?, updated_at = datetime('now') WHERE id = ?",
            (new_balance, self.account_id),
        )
        order_id = self.db.insert_paper_order(
            account_id=self.account_id,
            symbol=symbol,
            side=side_n,
            quantity=quantity,
            price=price,
            rating=rating,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            market_type=market_type,
        )
        log.info(
            "Paper %s %s qty=%.6f @ %.2f SL=%s TP1=%s → order_id=%s balance=%.2f",
            side_n,
            symbol,
            quantity,
            price,
            stop_loss,
            take_profit_1,
            order_id,
            new_balance,
        )
        return PaperFill(
            order_id=order_id,
            symbol=symbol,
            side=side_n,
            quantity=quantity,
            price=price,
            balance_after=new_balance,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            rating=rating,
        )


class LiveBrokerStub:
    """Live chưa bật — Phase 4 chỉ paper."""

    def execute_plan(self, plan: OrderPlan) -> None:
        raise NotImplementedError(
            "Live trading chưa bật. Phase 4 chỉ paper. "
            f"(plan approved={plan.approved})"
        )
