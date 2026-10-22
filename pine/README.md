# Pine Scripts — Trading Thesis

## Dùng file nào?

| File | Khi nào |
|------|---------|
| **`T3b_optimize_thongke.pine`** ← **DÙNG CÁI NÀY** | Sau khi T3 Gross lãi nhưng Net lỗ vì **phí** |
| `T3_wyckoff_pa_thongke.pine` | Bản T3 gốc (dễ bị phí ăn) |
| `T2_sd_thongke.pine` | S/D filter |
| `T1c_overlay_thongke.pine` | UX THỐNG KÊ ban đầu |

Phân tích số liệu T3: [`docs/thesis/optimize-from-t3-stats.md`](../docs/thesis/optimize-from-t3-stats.md)

## T3b sửa gì?

1. **Sàn SL tối thiểu** (ATR + % giá) → Qty không nổ  
2. **Bỏ lệnh** nếu phí ước tính > 25% risk  
3. Mặc định **Chỉ Spring/UT**, cooldown 36, volume ×1.5  
4. TP mặc định **2.5R** (Settings đổi lại **2R** nếu muốn giữ quyết định cũ)  
5. Dòng bảng **Phí / |Gross|** — mục tiêu < 100%

## Cách dán

1. Remove T3 cũ.  
2. **BTCUSDT.P · 5m** (Binance).  
3. Dán `T3b_optimize_thongke.pine` → Add to chart.  
4. So: Gross vs Tổng phí; Net có còn âm vì phí không.
