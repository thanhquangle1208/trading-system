# Quyết định thesis đã chốt

Cập nhật khi Tomas trả lời. Agent đọc file này trước khi viết Pine tiếp.

| Ngày | Mục | Quyết định |
|------|-----|------------|
| 2026-10-21 | Ưu tiên | Pine thesis trước; bot Phase 1 **hoãn** |
| 2026-10-21 | Script | Viết lại từ đầu |
| 2026-10-21 | Chart | **BINANCE:BTCUSDT.P** |
| 2026-10-21 | Vốn paper | **$10.000** |
| 2026-10-21 | Phương pháp | **S/D + Wyckoff + PA + Trend line** (4 trụ confluence) |
| 2026-10-21 | **OK phương pháp** | **Có** — Tomas duyệt |
| 2026-10-21 | TP | **2R** |
| 2026-10-21 | TF học | **5m** |
| 2026-10-21 | Volume | **Bắt buộc** trong điều kiện tín hiệu |

## Trạng thái bước

| Bước | Trạng thái |
|------|------------|
| T0 docs | Đã duyệt (cùng OK phương pháp) |
| T1 indicator | Đã viết; Tomas: **quá nhiều mũi tên** |
| T1b strategy | Có — nhưng panel dưới ≠ ảnh mẫu |
| T1c overlay THỐNG KÊ | OK UX; nhiều lệnh |
| T2 S/D filter | Xong |
| T3 Wyckoff/PA | OK UX; PnL fail vì phí |
| T3b Optimize | Xong (chống phí) |
| T3c WR-first | Quá siết → 0 lệnh |
| T3d Balanced | Xong |
| **T3e** | **Dùng** — `pine/T3e.pine` (đã bỏ Trendline) |
| TP | **1.5R** (ưu tiên WR) |
| Trendline | **Bỏ** (2026-10-23) — Tomas: không hiệu quả; bản cũ `T3e_trendline.pine` chỉ giữ tham khảo |
| 2026-10-23 | Scanner TG | Perp Binance→Bybit; TF H1/H4/D1/W1; điểm /10; scan 1 lần rồi watch; xem `docs/scanner/telegram-sd-alerts.md` |
| Học từ lệnh lãi | Doc `learn-from-winners.md` |
| Phân tích phí T3 | Doc `optimize-from-t3-stats.md` |
| Hướng WR60 | Doc `wr60-tp15-path.md` |
| Vì sao 0 lệnh T3c | Doc `why-zero-trades-t3c.md` |
