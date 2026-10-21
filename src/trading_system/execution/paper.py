"""Paper broker tối giản — ghi lệnh giả vào SQLite, chưa có risk engine đầy đủ."""

from __future__ import annotations

from dataclasses import dataclass

from trading_system.logging_setup import get_logger
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


class PaperBroker:
    """Giả lập mua/bán spot: trừ/cộng USDT theo giá × số lượng (đơn giản hóa Phase 1)."""

    def __init__(self, db: Database, account_id: int) -> None:
        self.db = db
        self.account_id = account_id

    def market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        rating: int | None = None,
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
            # Phase 1: bán chỉ cộng USDT (chưa theo dõi inventory coin đầy đủ)
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
        )
        log.info(
            "Paper %s %s qty=%.6f @ %.2f → order_id=%s balance=%.2f",
            side_n,
            symbol,
            quantity,
            price,
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
        )
