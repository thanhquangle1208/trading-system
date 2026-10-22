# Vì sao T3c = 0 lệnh? (dù thấy Sp / UT)

Tomas thấy kim cương **Sp** / **UT** và ô Supply/Demand, nhưng bảng **Tổng lệnh = 0**.

## Điểm then chốt

**Sp / UT trên chart ≠ đã vào lệnh.**

- `Sp` / `UT` chỉ = phát hiện Spring / Upthrust.  
- **Lệnh thật** cần thêm nhiều điều kiện AND. Thiếu 1 cái → **không vào**.

## T3c đã siết gì? (chi tiết)

| # | Lọc | T3c (siết) | Tác dụng |
|---|-----|------------|----------|
| 1 | Chỉ Spring/UT | Bắt buộc | Không vào chỉ vì chạm zone |
| 2 | PA reject wick | `requireReject=true`, bóng ≥ 1.5× | Nhiều Sp **không** đủ reject mạnh |
| 3 | Volume | ≥ SMA × **1.8** | Rất hay chặn |
| 4 | SuperTrend 5m | Phải cùng hướng | Sp xuống khi ST vẫn down → chặn LONG |
| 5 | HTF 15m | EMA đồng thuận | **Rất hay làm 0 lệnh** trên 5m |
| 6 | Chống dao rơi | 3 nến đỏ mạnh → cấm LONG | Spring thường **sau** chuỗi đỏ → **tự mâu thuẫn**, chặn gần hết Spring |
| 7 | Cooldown | 48 nến | Ít ảnh hưởng khi tổng = 0 từ đầu |
| 8 | Fee/SL cap | Bỏ lệnh phí cao / SL quá sát | Có thể nuốt nốt tín hiệu cuối |

→ Đặc biệt (#2 + #5 + #6) chồng nhau = **có Sp mà không có lệnh**.

## Hướng xử lý

1. **Dùng T3d** (`pine/T3d_balanced_wr.pine`) — đã nới mặc định:  
   - Reject **hoặc** Engulf  
   - Volume × **1.2**  
   - **Tắt** HTF + chống dao rơi (bật lại sau khi đã có lệnh)  
   - Cooldown 24  
   - Vẫn: Spring/UT + TP **1.5R** + sàn SL + fee cap  
   - Có dòng **Debug** góc phải dưới: báo vì sao Sp chưa thành lệnh  

2. Siết lại **từng lớp** sau khi đã có ≥ 15–20 lệnh: bật HTF → đo WR → bật knife → đo lại.

3. Chart học vẫn nên **BTCUSDT.P · 5m** (Binance), không Bitstamp Weekly/khác nếu đang so thesis.
