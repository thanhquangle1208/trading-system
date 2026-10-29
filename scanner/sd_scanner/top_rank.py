"""Xếp hạng tin đã noti cho lệnh /top — đa tiêu chí, pair chỉ là điểm cộng nhẹ."""

from __future__ import annotations

from .alert_history import AlertRecord

# Soft boost theo thanh khoản / độ quen thuộc — KHÔNG cố định thứ tự xếp hạng.
# Điểm này nhỏ so với confidence/depth/R:R/TF; alt bất kỳ vẫn có thể vào top 3.
_PAIR_SOFT: dict[str, float] = {
    "BTCUSDT": 1.5,
    "ETHUSDT": 1.3,
    "BNBUSDT": 1.1,
    "SOLUSDT": 1.0,
    "XRPUSDT": 0.8,
    "ADAUSDT": 0.7,
    "DOGEUSDT": 0.6,
    "AVAXUSDT": 0.6,
    "LINKUSDT": 0.6,
    "DOTUSDT": 0.5,
}


def _base_symbol(symbol: str) -> str:
    s = symbol.upper().replace(".P", "").replace("/", "")
    return s


def pair_soft_bonus(symbol: str) -> float:
    """Điểm cộng nhẹ (0–1.5). Cặp lạ = 0.3 nền — vẫn được xét đủ."""
    s = _base_symbol(symbol)
    if s in _PAIR_SOFT:
        return _PAIR_SOFT[s]
    # Token đòn bẩy kiểu 1000PEPE — nền thấp hơn majors nhưng không loại
    if s.startswith("1000") or s.startswith("1000000"):
        return 0.2
    return 0.35


def tf_bonus(timeframe: str) -> float:
    t = timeframe.upper()
    return {"W1": 2.0, "D1": 1.5, "H4": 0.8, "H1": 0.2}.get(t, 0.4)


def rr_bonus(rr: float | None) -> float:
    """R:R tốt được cộng; cap để R:R cực đại không thổi phồng ảo."""
    if rr is None or rr <= 0:
        return 0.0
    capped = min(float(rr), 5.0)  # trên 5R coi như đủ tốt
    return capped / 5.0 * 2.0  # tối đa +2.0


def bias_bonus(w1_bias: str | None) -> float:
    return 0.8 if w1_bias else 0.0


def score_alert(rec: AlertRecord) -> float:
    """
    Điểm tổng (càng cao càng đáng xem).

    Trọng số gần đúng:
    - Độ tin cậy ~ nhân 3.0  (chính)
    - Độ sâu     ~ nhân 2.0
    - R:R        ~ tới +2.0
    - Khung TF   ~ tới +2.0
    - Bias W1    ~ +0.8
    - Pair soft  ~ tới +1.5  (chỉ phụ, không quyết định cả bảng)
    """
    return (
        float(rec.confidence) * 3.0
        + float(rec.depth) * 2.0
        + rr_bonus(rec.rr)
        + tf_bonus(rec.timeframe)
        + bias_bonus(rec.w1_bias)
        + pair_soft_bonus(rec.symbol)
    )


def pick_top(
    records: list[AlertRecord],
    *,
    limit: int = 3,
) -> list[tuple[AlertRecord, float]]:
    """
    Một lần / cặp (giữ bản điểm cao nhất), rồi lấy `limit` điểm cao nhất.
    Mọi dự án/cặp đều được xét — không cố định BTC>ETH>…
    """
    best_by_sym: dict[str, tuple[AlertRecord, float]] = {}
    for rec in records:
        sc = score_alert(rec)
        key = _base_symbol(rec.symbol)
        prev = best_by_sym.get(key)
        if prev is None or sc > prev[1] or (sc == prev[1] and rec.ts > prev[0].ts):
            best_by_sym[key] = (rec, sc)

    ranked = sorted(best_by_sym.values(), key=lambda x: (-x[1], -x[0].ts))
    return ranked[:limit]


def score_breakdown(rec: AlertRecord) -> str:
    """Chuỗi ngắn giải thích (tiếng Việt) — cho newbie."""
    parts = [
        f"tin cậy {rec.confidence:.1f}",
        f"độ sâu {rec.depth:.1f}",
    ]
    if rec.rr is not None:
        parts.append(f"R:R {rec.rr:g}")
    parts.append(f"khung {rec.timeframe}")
    if rec.w1_bias:
        parts.append("có bias W1")
    pb = pair_soft_bonus(rec.symbol)
    if pb >= 1.0:
        parts.append("pair thanh khoản tốt")
    return ", ".join(parts)
