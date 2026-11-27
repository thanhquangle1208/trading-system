"""Một dòng vùng giá đọc từ Notion."""

from __future__ import annotations

from dataclasses import dataclass

STATUS_ACTIVE = "Đang theo dõi"
STATUS_EXPIRED = "Hết hiệu lực"
STATUS_STALE = "Cũ cần cập nhật"


@dataclass
class BuyZone:
    page_id: str
    token_name: str
    ticker: str
    zone_no: str
    lower: float | None
    upper: float | None
    invalidation: float | None
    status: str
    reference: str
    note: str
    link: str
    analysis_price: float | None = None
    analysis_date: str | None = None

    @property
    def active(self) -> bool:
        return self.status == STATUS_ACTIVE

    def skip_reason(self) -> str | None:
        """Lý do không xét vùng này. None = xét bình thường."""
        if not self.active:
            return f"trạng thái '{self.status or 'trống'}' — chỉ báo khi '{STATUS_ACTIVE}'"
        if not self.ticker:
            return "thiếu Ticker"
        if self.lower is None or self.upper is None:
            return "thiếu Giá dưới hoặc Giá trên"
        if self.lower <= 0 or self.upper <= 0:
            return "giá vùng phải là số dương"
        if self.lower == self.upper:
            return None
        return None

    def bounds(self) -> tuple[float, float]:
        assert self.lower is not None and self.upper is not None
        lo, hi = self.lower, self.upper
        if lo > hi:
            lo, hi = hi, lo
        return lo, hi
