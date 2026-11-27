"""Câu chữ tiếng Việt gửi Telegram. Văn bản thuần, không Markdown."""

from __future__ import annotations

import math
import re

from trading_system.zones.models import BuyZone

# Giữ đoạn ghi chú có các từ này (tokenomics / vesting / Z1–Z3).
_KEEP_NOTE = re.compile(
    r"(?i)\b("
    r"tokenomics|tokenomic|vesting|vest|unlock|unl|cliff|tge|"
    r"fdv|supply|emission|dilut|airdrop|allocation|alloc|"
    r"z\s*[123]|v[uù]ng\s*[123]"
    r")\b"
)
# Bỏ đoạn về mức vô hiệu / nhắc mua chung chung / chỉ lặp ticker.
_DROP_NOTE = re.compile(
    r"(?i)("
    r"v[oô] ?hi[eệ]u|"
    r"n[eế]n\s+ng[aà]y\s+đ[oó]ng|"
    r"07:00\s*vn|"
    r"gom\s+t[uừ]ng\s+ph[aầ]n|"
    r"ch[oờ]\s+n[eế]n\s+x[aá]c\s+nh[aậ]n"
    r")"
)
_SPLIT_NOTE = re.compile(r"(?<=[.!?…])\s+|\n+|;\s*")


def format_price(value: float) -> str:
    """55.000 / 60.850 / 0,00125 — dấu chấm nghìn, dấu phẩy thập phân."""
    if not math.isfinite(value):
        return "—"
    sign = "-" if value < 0 else ""
    number = abs(value)
    if number >= 100:
        if abs(number - round(number)) < 1e-6 * max(1.0, number):
            text = f"{int(round(number)):,}"
        else:
            text = f"{number:,.2f}".rstrip("0").rstrip(".")
    elif number >= 1:
        text = f"{number:,.4f}".rstrip("0").rstrip(".")
    else:
        text = f"{number:.8f}".rstrip("0").rstrip(".")
    return sign + text.replace(",", "X").replace(".", ",").replace("X", ".")


def useful_note(note: str, ticker: str = "", *, limit: int = 300) -> str:
    """Chỉ giữ đoạn liên quan tokenomics / vesting / Z1–Z3. Bỏ vô hiệu và câu thừa."""
    raw = " ".join((note or "").split()).strip()
    if not raw:
        return ""
    ticker_u = (ticker or "").strip().upper()
    parts = [p.strip(" .") for p in _SPLIT_NOTE.split(raw) if p.strip(" .")]
    kept: list[str] = []
    for part in parts:
        compact = part.strip()
        if not compact:
            continue
        if ticker_u and compact.upper() == ticker_u:
            continue
        if _DROP_NOTE.search(compact):
            continue
        if _KEEP_NOTE.search(compact):
            kept.append(compact)
    if not kept:
        return ""
    text = ". ".join(kept)
    if not text.endswith("."):
        text += "."
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def format_entry(zone: BuyZone, price: float) -> str:
    """Tin vào vùng: không nhắc mức vô hiệu; ghi chú chỉ tokenomics/vesting/Z."""
    lo, hi = zone.bounds()
    bits = [
        f"🟢 {zone.ticker} vào Vùng {zone.zone_no} ({format_price(lo)}–{format_price(hi)}).",
        f"Giá hiện tại: {format_price(price)}.",
    ]
    note = useful_note(zone.note, zone.ticker)
    if note:
        bits.append(f"Ghi chú: {note}")
    if zone.link.strip():
        bits.append(zone.link.strip())
    return " ".join(bits)


def format_approaching(zone: BuyZone, price: float, approaching_pct: float) -> str:
    _lo, hi = zone.bounds()
    pct = f"{approaching_pct:g}"
    bits = [
        (
            f"🟡 {zone.ticker} đang tiến gần Vùng {zone.zone_no} "
            f"(trong {pct}% phía trên {format_price(hi)})."
        ),
        f"Giá hiện tại: {format_price(price)}.",
    ]
    if zone.link.strip():
        bits.append(zone.link.strip())
    return " ".join(bits)


def format_invalidation(zone: BuyZone, daily_close: float) -> str:
    assert zone.invalidation is not None
    bits = [
        (
            f"🔴 {zone.ticker} – Vùng {zone.zone_no} hết hiệu lực: "
            f"nến ngày đóng {format_price(daily_close)} < {format_price(zone.invalidation)}. "
            f"Dừng mua vùng này, đánh giá lại."
        )
    ]
    if zone.link.strip():
        bits.append(zone.link.strip())
    return " ".join(bits)


def format_digest(
    rows: list[tuple[BuyZone, float, bool]],
    unpriced: list[str],
    *,
    hour: int,
    minute: int,
    watching: int,
) -> str:
    """rows: (zone, price, invalidated)."""
    lines = [f"📋 Bản tin {hour:02d}:{minute:02d} — giá đang nằm trong vùng gom:"]
    if watching == 0:
        lines.append("Không có vùng nào ở trạng thái Đang theo dõi.")
    elif not rows:
        lines.append("Không có giá nào đang nằm trong vùng đang theo dõi.")
    else:
        for zone, price, invalidated in rows:
            lo, hi = zone.bounds()
            line = (
                f"• {zone.ticker} Vùng {zone.zone_no}: {format_price(price)} "
                f"nằm trong {format_price(lo)}–{format_price(hi)}"
            )
            if invalidated:
                line += " — đã vô hiệu (nến ngày đóng dưới mức)"
            lines.append(line)
            if zone.link.strip():
                lines.append(f"  {zone.link.strip()}")
        lines.append(f"Tổng: {len(rows)} vùng.")
    if unpriced:
        shown = ", ".join(unpriced[:12])
        extra = f" (+{len(unpriced) - 12})" if len(unpriced) > 12 else ""
        lines.append(f"Không lấy được giá (bỏ qua): {shown}{extra}.")
    return "\n".join(lines)
