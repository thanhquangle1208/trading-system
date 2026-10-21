"""Template nội dung Telegram — channel, TF, display_name, chỉ báo, rating."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def rating_bar(rating: int | None, max_rating: int = 10) -> str:
    if rating is None:
        return ""
    r = max(0, min(max_rating, int(rating)))
    return "█" * r + "░" * (max_rating - r)


def format_signal_message(
    *,
    channel_name: str,
    timeframe: str,
    strategy_display_name: str,
    symbol: str,
    direction: str | None,
    score: float,
    rating: int | None,
    rating_label: str = "Độ tin cậy",
    indicator_labels: Sequence[str] | None = None,
    reason: str = "",
    include_rating_bar: bool = True,
    extra: Mapping[str, Any] | None = None,
) -> str:
    lines = [
        f"📢 {channel_name}",
        f"⏱ Timeframe: {timeframe}",
        f"📌 Method: {strategy_display_name}",
        f"🪙 {symbol} · {((direction or '') or 'n/a').upper()}",
        f"📊 Score: {score:.0f}/100",
    ]
    if rating is not None:
        bar = f" {rating_bar(rating)}" if include_rating_bar else ""
        lines.append(f"⭐ {rating_label}: {rating}/10{bar}")
    if indicator_labels:
        lines.append("🔧 Chỉ báo: " + ", ".join(indicator_labels))
    if reason:
        lines.append(f"ℹ️ {reason}")
    if extra:
        for k, v in extra.items():
            lines.append(f"· {k}: {v}")
    return "\n".join(lines)


def format_test_message(channel_name: str = "main") -> str:
    return format_signal_message(
        channel_name=channel_name,
        timeframe="H1",
        strategy_display_name="Confluence BTC Spot + Wyckoff",
        symbol="BTC/USDT",
        direction="long",
        score=75,
        rating=8,
        indicator_labels=["EMA 34/89", "Wyckoff cơ bản"],
        reason="Tin thử Phase 6 — không phải lệnh thật",
    )
