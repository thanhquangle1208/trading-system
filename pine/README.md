# Pine Scripts — Trading Thesis

Script dán vào **TradingView → Pine Editor**. Không chạy bằng Python.

## Đã chốt (Tomas)

| Mục | Giá trị |
|-----|---------|
| Phương pháp | S/D + Wyckoff + PA + Trend line |
| Chart | **BINANCE:BTCUSDT.P** |
| TF | **5m** |
| TP | **2R** (áp dụng từ bước hộp lệnh T4) |
| Volume | **Bắt buộc** trong tín hiệu |
| Vốn paper | $10.000 |

## Cách dán script (Tomas làm trên máy)

1. Mở [TradingView](https://www.tradingview.com/) → đăng nhập.  
2. Ô tìm symbol → gõ **BTCUSDT.P** → chọn **Binance** perpetual.  
3. Khung thời gian chọn **5**.  
4. Dưới chart bấm **Pine Editor**.  
5. Xóa code mẫu → mở file trong repo (vd. `T1_trendline_volume.pine`) → **copy toàn bộ** → dán vào editor.  
6. Bấm **Save** → **Add to chart**.  
7. Nếu báo lỗi đỏ: chụp màn hình gửi agent (copy dòng lỗi cũng được).

## File

| File | Bước | Việc |
|------|------|------|
| `T1_trendline_volume.pine` | **T1** | Pivot + trendline + bias + mũi tên (có lọc volume) |
| (sau) T2… | T2+ | S/D zones, Spring/PA, hộp lệnh, THỐNG KÊ |

## T1 xem được gì?

- Đường **teal** = hỗ trợ (uptrend lows)  
- Đường **cam** = kháng cự (downtrend highs)  
- Nền xanh nhạt = bias up; cam nhạt = bias down  
- Mũi tên **L / S** = tín hiệu thô T1 (chưa đủ 4 trụ — thiếu S/D + Wyckoff + PA)  
- Bảng góc phải: Bias, Volume OK, nhắc TP 2R / TF 5m  

Nếu mũi tên quá nhiều/ít: chỉnh input **Pivot**, **Gần trendline %**, hoặc **Volume ≥ SMA ×**.
