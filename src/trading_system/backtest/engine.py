"""
Backtest engine — multi-bar, không look-ahead.

Luật:
- Tín hiệu tại bar i chỉ dùng candles[0 : i+1]
- Vào lệnh tại open của bar i+1 (không dùng giá tương lai)
- Thoát theo high/low của các bar sau (SL/TP)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from trading_system.backtest.costs import CostModel
from trading_system.backtest.metrics import BacktestMetrics, compute_metrics, summarize_trades
from trading_system.backtest.portfolio import ClosedTrade, OpenPosition, Portfolio
from trading_system.data.base import Candle
from trading_system.indicators.atr import Atr
from trading_system.logging_setup import get_logger
from trading_system.risk.config import RiskConfig, load_risk_config
from trading_system.risk.engine import RiskEngine
from trading_system.signals.confluence import evaluate_strategy
from trading_system.signals.models import StrategySpec
from trading_system.signals.strategy_loader import load_strategy

log = get_logger("backtest.engine")


@dataclass
class BacktestResult:
    metrics: BacktestMetrics
    trades: list[dict[str, Any]]
    equity_curve: list[float]
    params: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "metrics": self.metrics.as_dict(),
            "trades": self.trades,
            "equity_curve": self.equity_curve,
            "params": self.params,
        }


class BacktestEngine:
    def __init__(
        self,
        *,
        strategy: StrategySpec | None = None,
        risk: RiskConfig | None = None,
        costs: CostModel | None = None,
        initial_balance: float = 1000.0,
        warmup_bars: int = 100,
        timeframe: str = "H1",
        market_type: str = "spot",
    ) -> None:
        self.strategy = strategy or load_strategy("btc_confluence_wyckoff.yaml")
        self.risk = risk or load_risk_config()
        self.costs = costs or CostModel()
        self.initial_balance = initial_balance
        self.warmup_bars = warmup_bars
        self.timeframe = timeframe
        self.market_type = market_type
        self.risk_engine = RiskEngine(self.risk)

    def run(self, candles: Sequence[Candle]) -> BacktestResult:
        if len(candles) <= self.warmup_bars + 2:
            raise ValueError(
                f"Cần > {self.warmup_bars + 2} nến, đang có {len(candles)}"
            )

        pf = Portfolio(balance=self.initial_balance)
        pending_entry_bar: int | None = None
        pending_signal = None

        # i = index của bar vừa đóng (tín hiệu)
        for i in range(self.warmup_bars, len(candles) - 1):
            bar = candles[i]
            # 1) Quản lý vị thế trên bar hiện tại (high/low) — trước khi tín hiệu mới
            self._manage_exits(pf, bar, i)

            # 2) Nếu có lệnh chờ từ bar trước → vào tại open bar này
            if pending_entry_bar == i and pending_signal is not None and pf.position is None:
                self._open_from_signal(pf, candles, i, pending_signal)
                pending_entry_bar = None
                pending_signal = None

            # 3) Tín hiệu chỉ với dữ liệu đến bar i (no look-ahead)
            window = candles[: i + 1]
            signal = evaluate_strategy(self.strategy, window, self.timeframe)
            if signal.fired and pf.position is None and pending_entry_bar is None:
                # Vào ở bar kế (i+1) open
                pending_entry_bar = i + 1
                pending_signal = signal

            pf.mark_equity(bar.close)

        # Bar cuối: chỉ quản lý thoát, không mở mới (không có bar sau)
        last_i = len(candles) - 1
        self._manage_exits(pf, candles[last_i], last_i)
        if pf.position:
            self._force_close(pf, candles[last_i].close, last_i, "end_of_data")
        pf.mark_equity(candles[last_i].close)

        metrics = compute_metrics(pf, self.initial_balance)
        log.info(
            "Backtest xong: trades=%s PnL=%.2f return=%.1f%% DD=%.1f%% fees=%.2f",
            metrics.n_trades,
            metrics.net_pnl,
            metrics.return_pct,
            metrics.max_drawdown_pct,
            metrics.total_fees,
        )
        return BacktestResult(
            metrics=metrics,
            trades=summarize_trades(pf.trades),
            equity_curve=list(pf.equity_curve),
            params={
                "strategy_id": self.strategy.id,
                "score_threshold": self.strategy.score_threshold,
                "warmup_bars": self.warmup_bars,
                "fee_bps": self.costs.fee_bps,
                "slippage_bps": self.costs.slippage_bps,
                "timeframe": self.timeframe,
            },
        )

    def _open_from_signal(
        self,
        pf: Portfolio,
        candles: Sequence[Candle],
        entry_bar: int,
        signal,
    ) -> None:
        window = candles[:entry_bar]  # ATR/risk: không gồm bar hiện tại chưa đóng đủ? 
        # Dùng đến bar trước entry (entry tại open) — window candles[:entry_bar] = bars 0..entry_bar-1
        # An toàn hơn: dùng tới entry_bar-1; nếu quá ngắn bỏ qua
        if entry_bar < self.warmup_bars:
            return
        hist = candles[:entry_bar]
        atr_val = Atr().compute(hist).values.get("atr")
        if not atr_val:
            return
        open_px = candles[entry_bar].open
        plan = self.risk_engine.plan_order(
            signal=signal,
            entry_price=open_px,
            atr=float(atr_val),
            balance=pf.balance,
            open_orders=1 if pf.position else 0,
            starting_balance=self.initial_balance,
            market_type=self.market_type,
        )
        if not plan.approved or plan.quantity <= 0 or plan.stop_loss is None:
            return

        fill_px = self.costs.apply_entry(plan.entry_price, plan.side)
        notional = plan.quantity * fill_px
        fee = self.costs.fee_usdt(notional)
        if plan.side == "buy" and notional + fee > pf.balance:
            return

        pf.balance -= fee
        if plan.side == "buy":
            pf.balance -= notional
        else:
            # short spot đơn giản: không implement inventory — chỉ long trong Phase 5 spot
            if plan.side != "buy":
                return

        pf.total_fees += fee
        pf.position = OpenPosition(
            side="buy",
            qty=plan.quantity,
            entry=fill_px,
            stop_loss=plan.stop_loss,
            take_profit_1=plan.take_profit_1 or fill_px,
            take_profit_2=plan.take_profit_2 or fill_px,
            partial_tp_pct=plan.partial_tp_pct,
            rating=plan.rating,
            entry_bar=entry_bar,
        )

    def _manage_exits(self, pf: Portfolio, bar: Candle, bar_index: int) -> None:
        pos = pf.position
        if not pos:
            return
        # Funding (spot = 0)
        notional = (pos.remaining_qty or 0) * bar.close
        funding = self.costs.funding_usdt(notional)
        if funding:
            pf.balance -= funding
            pf.total_fees += funding

        # SL trước (conservative)
        if bar.low <= pos.stop_loss:
            self._close_qty(pf, pos.remaining_qty or 0, pos.stop_loss, bar_index, "sl")
            return
        # TP1 partial
        if not pos.partial_done and bar.high >= pos.take_profit_1:
            part = min(pos.qty * pos.partial_tp_pct, pos.remaining_qty or 0)
            if part > 0:
                self._close_qty(pf, part, pos.take_profit_1, bar_index, "tp1")
                if pf.position:
                    pf.position.partial_done = True
                    pf.position.stop_loss = pf.position.entry  # về hòa vốn sau TP1
        # TP2 phần còn lại
        if pf.position and bar.high >= pf.position.take_profit_2:
            self._close_qty(
                pf,
                pf.position.remaining_qty or 0,
                pf.position.take_profit_2,
                bar_index,
                "tp2",
            )

    def _close_qty(
        self,
        pf: Portfolio,
        qty: float,
        raw_exit: float,
        bar_index: int,
        reason: str,
    ) -> None:
        pos = pf.position
        if not pos or qty <= 0:
            return
        exit_px = self.costs.apply_exit(raw_exit, pos.side)
        notional = qty * exit_px
        fee = self.costs.fee_usdt(notional)
        pnl = (exit_px - pos.entry) * qty - fee
        pf.balance += qty * exit_px - fee
        pf.total_fees += fee
        pf.trades.append(
            ClosedTrade(
                side=pos.side,
                qty=qty,
                entry=pos.entry,
                exit=exit_px,
                pnl=pnl,
                fees=fee,
                rating=pos.rating,
                exit_reason=reason,
                entry_bar=pos.entry_bar,
                exit_bar=bar_index,
            )
        )
        pos.remaining_qty = (pos.remaining_qty or 0) - qty
        if (pos.remaining_qty or 0) <= 1e-12:
            pf.position = None

    def _force_close(self, pf: Portfolio, price: float, bar_index: int, reason: str) -> None:
        if pf.position:
            self._close_qty(pf, pf.position.remaining_qty or 0, price, bar_index, reason)
