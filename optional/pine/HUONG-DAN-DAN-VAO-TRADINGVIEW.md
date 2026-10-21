# Hướng dẫn dán Pine vào TradingView (cho newbie)

## Pine dùng để làm gì?

Để **soi** EMA / RSI / confluence / Wyckoff trên chart TradingView.  
Bot mua–bán paper của bạn vẫn chạy bằng **Python** trên máy — Pine **không** điều khiển bot.

---

## Bạn cần gì?

- Tài khoản TradingView (bản free cũng được để thử)
- File trong thư mục `optional/pine/` (repo trading-system)

---

## Bước 1 — Mở chart BTC

1. Vào [tradingview.com](https://www.tradingview.com) và đăng nhập  
2. Mở biểu đồ **BTCUSDT** (spot Bybit/Binance đều được để soi)  
3. Chọn khung thời gian bạn hay dùng (vd. **H1**)

**Để làm gì?** Có chỗ nhìn giá.  
**Tác dụng:** Script sẽ vẽ lên chart này.

---

## Bước 2 — Mở Pine Editor

1. Ở dưới cửa sổ chart, bấm **Pine Editor** (nếu không thấy: menu dưới cùng)  
2. Bấm **Open** → **New blank indicator** (chỉ báo trống)

**Để làm gì?** Tạo chỗ dán code.  
**Tác dụng:** TradingView chạy đúng ngôn ngữ Pine.

---

## Bước 3 — Copy một file `.pine`

Trong repo, mở một file, ví dụ:

- `TS_EMA_RSI.pine` — đường EMA + bảng RSI (dễ bắt đầu)  
- `TS_Confluence_Basic.pine` — điểm confluence (ô riêng dưới chart)  
- `TS_Wyckoff_Basic.pine` — vùng range + Spring / Upthrust  

1. **Ctrl+A** chọn hết → **Ctrl+C** copy  
2. Trong Pine Editor: **Ctrl+A** xóa mẫu → **Ctrl+V** dán  
3. Bấm **Save** (đặt tên tùy bạn)  
4. Bấm **Add to chart**

**Để làm gì?** Đưa script lên chart.  
**Tác dụng:** Thấy đường / hình / bảng số trên TV.

---

## Bước 4 — Xem gì trên chart?

| Script | Bạn sẽ thấy |
|--------|-------------|
| EMA + RSI | 2 đường EMA; nền xanh/đỏ nhẹ; bảng RSI góc |
| Confluence | Đường điểm 0–100; nền xanh khi ≥ ngưỡng 60 |
| Wyckoff | Dải range; mũi Spring / UT |

Nếu không thấy: kiểm tra đã **Add to chart**, đúng khung H1, và script **overlay** (Wyckoff/EMA) vs panel riêng (Confluence).

---

## Bước 5 — (Tuỳ chọn) Bật Alert trên TV

Trên chart → chuột phải indicator → **Add alert on…**  
Chọn điều kiện (vd. EMA cross). Alert TV **không** tự đặt lệnh bot Python trừ khi sau này bạn nối webhook (chưa làm).

---

## Lưu ý quan trọng

1. Số liệu Pine **có thể khác** bot Python (công thức / nến / sàn khác nhau) — dùng để **soi**, không copy 100% lệnh bot.  
2. Không dán API key / `.env` vào Pine.  
3. Làm xong 1 script rồi mới thử script tiếp theo cho đỡ rối.

---

## Xong bước nào thì báo agent?

Trả lời ngắn:

1. “Đã add EMA lên chart”  
2. “Bị lỗi … (chụp / copy dòng đỏ)”  
3. “Chưa biết mở Pine Editor”
