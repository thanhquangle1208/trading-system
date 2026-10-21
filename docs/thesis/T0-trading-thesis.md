# T0 — Trading Thesis (chốt trước khi viết Pine)

**Trạng thái:** Bản nháp chờ Tomas duyệt. Chưa có script Pine trong repo.

Mục tiêu giai đoạn này: **làm thesis trên TradingView giống ảnh** (hộp lệnh + bảng THỐNG KÊ), **hoãn bot / Telegram / Bybit API**.

**Phương pháp giao dịch (2026-10-21):** **Supply/Demand + Wyckoff + Price Action + Trend line** (confluence). Chi tiết: [`method-sd-wyckoff-pa.md`](./method-sd-wyckoff-pa.md).

---

## 1. Câu hỏi “tích hợp vào chart TV” — trả lời ngắn

TradingView **chỉ chạy code của chính nó**, gọi là **Pine Script**.

| Loại code | Có vẽ được lên chart TV như ảnh? |
|-----------|----------------------------------|
| **Pine Script** (trong Pine Editor của TV) | **Có** — mũi tên, hộp LONG/SHORT, bảng THỐNG KÊ, Supply/Demand |
| **Python bot** (máy bạn / server) | **Không** — bot đọc giá, đặt lệnh, gửi Telegram; **không** “nhét” được vào chart TV |

**Vậy giờ mình làm gì?**  
→ Viết **script Pine từ đầu**, dán vào TradingView, gắn lên chart **BINANCE:BTCUSDT.P**.  
Đó chính là “tích hợp vào chart như ảnh”.

Hình đơn giản:

```
Bạn mở TradingView
    → mở chart BTCUSDT.P
    → dán script Pine
    → TV tự vẽ: tín hiệu + hộp lệnh + bảng thống kê
```

Python bot = **bước sau**, khi thesis đã rõ và bạn muốn lệnh thật / paper ngoài TV.

---

## 2. Quyết định đã chốt (2026-10-21)

| Mục | Quyết định |
|-----|------------|
| Ưu tiên | **Thesis / Pine trước** — bot Phase 1 **hoãn** |
| Script | **Viết lại từ đầu** (không dùng bản cũ) |
| Logic | **Vừa làm vừa research** (bắt đầu đơn giản, chỉnh dần) |
| Vốn paper trong thesis | **$10.000** |
| Chart | **BINANCE:BTCUSDT.P** (perp) |
| Khung thời gian học | Bắt đầu **5m** (như ảnh); sau có thể thử M15/H1 |
| Sàn bot sau này | Vẫn hướng Bybit — **không làm lúc này** |

---

## 3. Bản thesis khởi điểm — 4 trụ confluence

Đây **không** phải luật cuối. Chi tiết đầy đủ + bảng Spring/UT/PA: [`method-sd-wyckoff-pa.md`](./method-sd-wyckoff-pa.md).

| Trụ | Vai trò trong lệnh |
|-----|-------------------|
| **Trend line** | Chỉ hướng + hỗ trợ/kháng cự động |
| **Supply / Demand** | Nơi ưu tiên vào (Demand=LONG, Supply=SHORT) |
| **Wyckoff (subset)** | Spring / Upthrust / LPS + đọc cung–cầu |
| **Price Action** | Nến xác nhận tại vùng confluence |

**Vào lệnh:** cần **đồng thuận** (đề xuất ≥ 3/4 trụ). Không vào chỉ vì một nến đẹp giữa chart.

### 3.1 Thoát lệnh / vốn / phí

| Thành phần | Đề xuất v0 |
|------------|------------|
| SL | Ngoài zone / ngoài Spring–UT |
| TP | Theo **R** (chờ Tomas chọn 2R / 3R / 5R) |
| Đảo chiều | Đóng hết rồi mở chiều mới |
| Vốn | $10.000 |
| Risk / lệnh | ~1% vốn |
| Qty | Từ khoảng Entry→SL và % risk |
| Phí | Ước tính % taker Binance Futures → Gross vs Net |

### 3.2 Hiển thị (giống ảnh)

1. Trend line + ô Supply / Demand  
2. Mũi tên vào / ra  
3. Hộp lệnh VN: Entry, SL, TP, Qty, phí, Gross/Net, WIN/LOSS  
4. Bảng **THỐNG KÊ**  

---

## 4. Lộ trình làm (sau khi Tomas OK phương pháp + T0)

| Bước | Việc | Sản phẩm |
|------|------|----------|
| **T0** | Chốt T0 + method S/D–Wyckoff–PA | Docs đã duyệt |
| **T1** | Pine: pivot + trend line + hướng | Đường trend + mũi tên thô |
| **T2** | Pine: S/D zones | Ô Supply/Demand |
| **T3** | Pine: Spring/UT + PA → tín hiệu confluence | Tín hiệu “đúng thesis” |
| **T4** | Hộp lệnh VN + SL/TP/Qty/phí | Giống ảnh |
| **T5** | Bảng THỐNG KÊ | Panel góc phải |
| **T6** | Research chỉnh trên BTCUSDT.P | Thesis ổn hơn |
| **Sau** | Bot Python / Bybit / Telegram | Chỉ khi Tomas nói OK |

Mỗi bước: **đề xuất → Tomas OK → mới code**.

---

## 5. Việc Tomas làm trên máy (không cần biết code)

1. Mở [TradingView](https://www.tradingview.com/) → đăng nhập.  
2. Tìm symbol **BTCUSDT.P** (Binance).  
3. Chọn khung **5**.  
4. Mở **Pine Editor** (dưới chart) → khi có script, dán vào → **Add to chart**.  
5. Xem Strategy Tester / bảng THỐNG KÊ trên chart.

Agent sẽ gửi script từng bước; bạn chỉ cần copy–paste.

---

## 6. Còn mở (chờ Tomas — xem thêm method §10)

- TP mặc định: **2R / 3R / 5R**?  
- TF học: giữ **5m** hay bắt đầu **15m** (ít nhiễu)?  
- Volume bắt buộc ngay hay để sau?  
- Tham số pivot / độ rộng zone — chỉnh khi có Pine  

---

## English summary

Pause bot. Thesis method: **Supply/Demand + Wyckoff (subset) + Price Action + Trend lines** with confluence. Pine from scratch on BINANCE:BTCUSDT.P, $10k. Full Wyckoff phases come gradually; automate a practical subset first.
