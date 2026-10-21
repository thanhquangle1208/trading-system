# T0 — Trading Thesis (chốt trước khi viết Pine)

**Trạng thái:** Bản nháp chờ Tomas duyệt. Chưa có script Pine trong repo.

Mục tiêu giai đoạn này: **làm thesis trên TradingView giống ảnh** (hộp lệnh + bảng THỐNG KÊ), **hoãn bot / Telegram / Bybit API**.

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

## 3. Bản thesis khởi điểm (đơn giản — sẽ chỉnh khi research)

Đây **không** phải luật cuối. Mục đích: có khung để viết Pine T1, rồi bạn và agent chỉnh.

### 3.1 Xu hướng (trend filter)

- Dùng 2 đường theo giá (kiểu trailing / ATR channel — chi tiết chọn khi viết Pine).
- **Chỉ LONG** khi xu hướng tăng; **chỉ SHORT** khi xu hướng giảm.
- Đảo chiều: đóng lệnh cũ trước khi mở lệnh ngược (“Close Long before Short” như ảnh).

### 3.2 Vào lệnh (entry) — phiên bản v0

Khi vừa research: bắt đầu bằng **1–2 điều kiện**, ví dụ:

- Giá cắt / phản ứng với đường trend **và**
- (tuỳ chọn sau) gần vùng Demand (LONG) / Supply (SHORT).

Supply/Demand zones: **T4** (sau khi đã có hộp lệnh + thống kê).

### 3.3 Thoát lệnh (exit)

| Thành phần | Đề xuất v0 | Ghi chú |
|------------|------------|---------|
| SL | Theo ATR hoặc khoảng cách cố định từ entry | Có thể đổi |
| TP | Theo **R** (vd. 2R–5R như ảnh có “TP 5R”) | Chỉnh được trên input |
| Đảo chiều | Đóng hết rồi mở chiều mới | Giống ảnh |

### 3.4 Quy mô lệnh (Qty) & phí

| Mục | Đề xuất v0 |
|-----|------------|
| Vốn | $10.000 |
| Risk / lệnh | ~1% vốn (đổi được) |
| Qty | Tính từ khoảng cách Entry→SL và % risk |
| Phí | Ước tính % (vd. taker Binance Futures) để ra Gross vs Net |

### 3.5 Hiển thị (giống ảnh)

1. Mũi tên vào / ra lệnh  
2. Hộp lệnh VN: Entry, SL, TP, Qty, phí, Gross/Net, WIN/LOSS  
3. Bảng **THỐNG KÊ**: vốn, số lệnh, winrate, phí, PF, Max DD…  
4. (Sau) ô Supply / Demand  

---

## 4. Lộ trình làm (sau khi Tomas OK T0)

| Bước | Việc | Sản phẩm |
|------|------|----------|
| **T0** | Chốt tài liệu này | File này đã duyệt |
| **T1** | Pine: trend + tín hiệu mũi tên | Chart có Long/Short signal |
| **T2** | Pine: SL/TP/Qty + hộp lệnh VN | Hộp giống ảnh |
| **T3** | Pine: bảng THỐNG KÊ | Panel góc phải |
| **T4** | (Tuỳ chọn) Supply / Demand | Zones như ảnh |
| **T5** | Research + chỉnh rule trên backtest TV | Thesis “chuẩn” hơn |
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

## 6. Còn mở (research dần — không chặn T1)

- Công thức trend chính xác (ATR length, multiplier…)  
- Entry trigger cụ thể (break, pullback, zone…)  
- TP mặc định bao nhiêu R  
- Phí % chính xác theo Binance  
- Có làm zone Supply/Demand từ đầu hay để T4  

---

## English summary

Pause bot. Build TradingView **Pine Script from scratch** so visuals match the screenshot (trade boxes + THỐNG KÊ). Capital $10k; chart BINANCE:BTCUSDT.P. Logic starts simple and is refined while researching. Python cannot draw on TV charts; Pine is the integration path.
