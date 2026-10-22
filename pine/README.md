# Pine Scripts — Trading Thesis

## Dùng file nào?

| File | Khi nào |
|------|---------|
| **`T2_sd_thongke.pine`** ← **DÙNG CÁI NÀY** | T2: ô Supply/Demand + ít lệnh hơn + THỐNG KÊ trên chart |
| `T1c_overlay_thongke.pine` | Bản trước (chưa lọc S/D — nhiều lệnh) |
| `T1b_strategy_thongke.pine` | Strategy Tester panel dưới (không phải ảnh mẫu) |
| `T1_trendline_volume.pine` | Chỉ trendline (cũ) |

## T2 lọc lệnh thế nào?

Chỉ vào lệnh khi **đủ cả**:

1. **Bias** SuperTrend đúng hướng (up → chỉ LONG, down → chỉ SHORT)  
2. Giá **chạm Demand** (LONG) hoặc **Supply** (SHORT)  
3. **Volume** ≥ SMA × hệ số  
4. Nến xác nhận (xanh/đỏ) — bật mặc định  
5. **Cooldown** giữa 2 lệnh  

→ Ít lệnh hơn T1c; zone **fresh** hết hạn sau khi đã trade.

## Cách dán T2

1. **Remove** T1c / script cũ trên chart.  
2. Chart: **BINANCE:BTCUSDT.P** · khung **5** (đừng test thesis trên coin lạ / TF khác nếu đang so với ảnh mẫu).  
3. Dán toàn bộ `T2_sd_thongke.pine` → Add to chart.  
4. Thấy: ô xanh **Demand** / cam **Supply**, bảng **THỐNG KÊ** góc phải, hộp WIN/LOSS.  
5. Nếu vẫn nhiều lệnh: tăng `Cooldown`, tăng `Pivot zone`, tăng `Volume ≥ SMA ×`.

## Đã chốt

Vốn $10k · TP **2R** · volume bắt buộc · phương pháp S/D + Wyckoff + PA + Trend.
