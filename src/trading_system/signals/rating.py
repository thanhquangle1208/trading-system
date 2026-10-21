"""Tính rating Độ tin cậy 1–10 từ score confluence."""

from __future__ import annotations


def confidence_rating(
    score: float,
    score_max: float = 100.0,
    *,
    fired: bool,
) -> int | None:
    """
    Nhãn: Độ tin cậy — số cao = tin hơn.
    Chỉ trả rating khi tín hiệu fired.
    Công thức đơn giản: map score → 1..10 (tối thiểu 6 khi vừa đủ ngưỡng ~60).
    """
    if not fired:
        return None
    if score_max <= 0:
        return 1
    ratio = max(0.0, min(1.0, score / score_max))
    # 0.6 → ~6, 1.0 → 10
    rating = int(round(ratio * 10))
    return max(1, min(10, rating))
