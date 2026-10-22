# Pine Scripts — Trading Thesis

Script dán vào **TradingView → Pine Editor**. Không chạy bằng Python.

## Đã chốt (Tomas)

| Mục | Giá trị |
|-----|---------|
| Phương pháp | S/D + Wyckoff + PA + Trend line |
| Chart | **BINANCE:BTCUSDT.P** |
| TF | **5m** |
| TP | **2R** |
| Volume | **Bắt buộc** |
| Vốn paper | $10.000 |

## Nên dùng file nào?

| File | Khi nào |
|------|---------|
| **`T1b_strategy_thongke.pine`** ← **dùng cái này** | Ít lệnh hơn; mỗi mũi tên = 1 lệnh có SL/TP; hộp PnL; bảng **THỐNG KÊ** giống ảnh mẫu |
| `T1_trendline_volume.pine` | Bản cũ (nhiều mũi tên, chỉ báo tín hiệu) — để tham khảo |

## Cách dán (T1b) — quan trọng

1. Symbol đúng: **BTCUSDT.P** (Binance), **không** dùng Bitstamp Weekly để học thesis.  
2. Khung: **5** (5 phút).  
3. **Gỡ** bản T1b cũ trên chart (nút … cạnh tên indicator → Remove).  
4. Pine Editor → **xóa hết** → dán lại toàn bộ file mới → **Save** → **Add to chart**.  
5. Bảng **THỐNG KÊ** nằm **góc phải trên** (tím đậm, chữ to).  
6. Nếu vẫn không thấy: mở Settings (bánh răng) của script → nhóm **Hiển thị** → bật **Bảng THỐNG KÊ** → thử đổi **Vị trí bảng** sang `Middle right`.  
7. Tab **Strategy Tester** (dưới chart) vẫn có số liệu ngay cả khi bảng bị che.

Nếu vẫn còn nhiều lệnh: tăng **Cooldown**, tăng **Volume ≥ SMA ×**, hoặc tăng **ATR multiplier**.

## Học từ lệnh lãi

Xem [`docs/thesis/learn-from-winners.md`](../docs/thesis/learn-from-winners.md): nhìn hộp WIN → tìm điểm chung → bảo agent thêm lọc.
