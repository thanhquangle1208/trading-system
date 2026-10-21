"""Phí / slippage / funding giả lập."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CostModel:
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    funding_bps_per_bar: float = 0.0

    def apply_entry(self, price: float, side: str) -> float:
        """Giá vào sau slippage (mua đắt hơn, bán rẻ hơn)."""
        slip = price * (self.slippage_bps / 10_000.0)
        if side in ("buy", "long"):
            return price + slip
        return price - slip

    def apply_exit(self, price: float, side: str) -> float:
        slip = price * (self.slippage_bps / 10_000.0)
        # Đóng long = bán → giá thấp hơn; đóng short = mua → giá cao hơn
        if side in ("buy", "long"):
            return price - slip
        return price + slip

    def fee_usdt(self, notional: float) -> float:
        return abs(notional) * (self.fee_bps / 10_000.0)

    def funding_usdt(self, notional: float) -> float:
        return abs(notional) * (self.funding_bps_per_bar / 10_000.0)
