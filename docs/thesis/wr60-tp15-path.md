# Hướng WR ~60% — TP 1.5R

**Tomas chọn (2026-10-22):** ưu tiên win rate, cho phép **TP = 1.5R** (dễ chạm TP hơn so với 2R).

Script: `pine/T3c_wr60_tp15.pine`

## Luật vào lệnh (AND — thiếu 1 cái = không vào)

1. SuperTrend 5m đúng hướng  
2. **Spring** (LONG) hoặc **Upthrust** (SHORT) tại S/D  
3. **Reject wick** mạnh (mặc định; không chỉ engulf)  
4. Volume ≥ SMA × 1.8  
5. Bias khung **15m** (HTF) cùng hướng  
6. Không vào kiểu dao rơi / đuổi giá (3 nến ngược mạnh)  
7. Cooldown 48 nến + sàn SL + fee cap (từ T3b)

## Mục tiêu đọc bảng

| Chỉ số | Mục tiêu |
|--------|----------|
| Win Rate | ~**60%** (xanh khi ≥ 60) |
| Tổng lệnh | Thường **ít hơn** T3 — bình thường |
| Net LN | > 0 |
| Phí / \|Gross\| | < 100% |

## Lưu ý

- Không đảm bảo 60% mọi giai đoạn; cần mẫu đủ lệnh (nên ≥ 15–20).  
- Chart học: **BINANCE:BTCUSDT.P · 5m**.  
- Muốn quay lại TP 2R: Settings → TP (R) = 2 (WR có thể giảm).
