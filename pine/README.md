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

## Cách dán (T1b)

1. TradingView → symbol **BTCUSDT.P** (Binance) → khung **5**  
2. **Pine Editor** → xóa code cũ → dán toàn bộ `T1b_strategy_thongke.pine`  
3. **Save** → **Add to chart**  
4. Góc phải: bảng **THỐNG KÊ**  
5. Trên nến: hộp LONG/SHORT + khi đóng hiện WIN/LOSS  
6. Tab **Strategy Tester** (dưới chart) để đối chiếu số liệu  

Nếu vẫn còn nhiều lệnh: tăng **Cooldown**, tăng **Volume ≥ SMA ×**, hoặc tăng **ATR multiplier**.

## Học từ lệnh lãi

Xem [`docs/thesis/learn-from-winners.md`](../docs/thesis/learn-from-winners.md): nhìn hộp WIN → tìm điểm chung → bảo agent thêm lọc.
